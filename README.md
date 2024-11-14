Backend framework for Archgem iOS app


temp:

import SwiftUI
import MapKit
import CoreLocation

struct HomeUIView: View {
    @ObservedObject var viewModel = HomeViewModel()
    @State private var locationSearch = LocationSearch(completer: .init())
    @State private var showingFilterPopup = false
    @State private var showingProfilePopup = false
    @State private var showingGemDialogue = false
    @State private var searchPresented = true
    @State private var searchRes:[SearchResult]?
    private var camPosition:MapCameraPosition = .userLocation(fallback:.automatic)
    @State var displayedGems:[Gem]?
    @EnvironmentObject var locationManager:LocationManager
    @Namespace var mainMapScope
    
    private var userLoc: CLLocationCoordinate2D? {
        return locationManager.lastLocation?.coordinate
    }
    
    var body: some View {
        
        ZStack(alignment: .top) {
                        
            Map(initialPosition: camPosition, scope: mainMapScope) {
                UserAnnotation()
                if (displayedGems != nil) {
                    ForEach(displayedGems!, id:\.id) {
                        gem in
                        Annotation(gem.name, coordinate: CLLocationCoordinate2D(latitude: gem.lat, longitude: gem.long)) {
                            Image("GemPin").padding(-40)
                                .onTapGesture {
                                    self.showingGemDialogue.toggle()
                                }
                                .sheet(isPresented: $showingGemDialogue) {
                                    GemPopupView(isPresented: $showingGemDialogue, gem: gem)
                                }
                        }
                    }
                }
            }
            
            
            .overlay(alignment: .topTrailing) {
                //map tools
                VStack {
                    MapUserLocationButton(scope: mainMapScope)
                    MapPitchToggle(scope: mainMapScope).mapControlVisibility(.visible)
                    MapCompass(scope:mainMapScope).mapControlVisibility(.visible)
                }
                .padding(.horizontal, 17)
                .padding(.top, 80)
                .buttonBorderShape(.circle)
            }
            .mapScope(mainMapScope)
            .mapStyle(.standard(elevation: .realistic))
            
            .onMapCameraChange {//populate view area with nearby gems
                position in
                Task {
                    if let gems = await viewModel.Search(position: position.region) {
                        displayedGems = gems
                    } else {
                        
                    }
                }
            }
                HStack(alignment: .top) {
                        // Filter Button
                        Button(action: {
                            self.showingFilterPopup.toggle()
                        }) {
                            Image(systemName: "line.horizontal.3.decrease.circle")
                                .foregroundColor(Color.gray)
                        }
                        
                        .padding()
                        .background(Color.white.opacity(1))
                        .cornerRadius(8)
                        .shadow(radius: 3)
                        .sheet(isPresented: $showingFilterPopup) {
                            FilterPopupView(isPresented: $showingFilterPopup)
                        }
                    
                        // Search Sheet
                        /*.sheet(isPresented: $searchPresented) {
                            SearchSheet(searchResults: $searchRes)
                        }*/
                        Spacer()
                        
                        // Profile Button
                        Button(action: {
                            self.showingProfilePopup.toggle()
                        }) {
                            Image(systemName: "person.crop.circle")
                                .foregroundColor(.black)
                        }
                        .padding()
                        .background(Color.white.opacity(1))
                        .cornerRadius(8)
                        .shadow(radius: 3)
                        .sheet(isPresented: $showingProfilePopup) {
                            ProfilePopupView(isPresented: $showingProfilePopup)
                        }
                    }
                .padding(.horizontal)
        }

        
    }
}

struct FilterPopupView: View {
    @Binding var isPresented: Bool

    var body: some View {
        VStack {
            Spacer()
            Text("Filter Options")
            Spacer()
            Button {
                isPresented = false
            }label: {
                Text("Cancel")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct ProfilePopupView: View {
    @Binding var isPresented: Bool

    var body: some View {
        VStack {
            Spacer()
            Text("Profile Options")
            Spacer()
            Button {
                isPresented = false
            }label: {
                Text("Cancel")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct GemPopupView: View {
    @Binding var isPresented: Bool
    @State var gem: Gem
    var body: some View {
        VStack {
            Spacer()
            Text(gem.description!)
            Spacer()
            Button {
                isPresented = false
            }label: {
                Text("Cancel")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct HomeUIView_Previews: PreviewProvider {
    static var previews: some View {
        HomeUIView()
    }
}

____________

import Foundation
import SwiftUI
import MapKit

struct SearchSheet: View {
    @State private var locationSearch = LocationSearch(completer: .init())
    @State private var search: String = ""
    @Binding var searchResults: [SearchResult]?
    
    var body: some View {
        VStack {
            HStack {
                Image(systemName:"magnifyingglass")
                TextField("Search for Location or Gem", text: $search)
                    .onSubmit {
                        Task {
                            searchResults = (try await locationSearch.search(with: search))
                        }
                    }
            }.modifier(TextFieldBG())
            
            List {
                ForEach(locationSearch.completions) {
                    completion in
                    
                    Button(action:{}) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(completion.title)
                                .font(.headline)
                                .fontDesign(.rounded)
                            Text(completion.subTitle)
                        }
                    }
                    .listRowBackground(Color.clear)
                }
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
        }
        
        .onChange(of: search) {
            locationSearch.update(queryFragment: search)
        }
        .padding(12)
        .presentationDetents([.height(100), .medium])
        .presentationBackground(.regularMaterial)
        .presentationBackgroundInteraction(.enabled(upThrough: .large))
        .interactiveDismissDisabled()
    }
}

struct TextFieldBG: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(12)
            .background(.gray.opacity(0.1))
            .presentationCornerRadius(20)
            .clipShape(.rect(cornerRadius: 20))
            .foregroundStyle(.primary)
            
    }
}


_____________

import MapKit

struct SearchResult: Identifiable, Hashable {
    let id = UUID()
    let title: String
    let subTitle: String
    let loc: CLLocationCoordinate2D
    
    static func == (lhs:SearchResult, rhs:SearchResult) -> Bool {
        lhs.id == rhs.id
    }
    
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}

@Observable
class LocationSearch: NSObject, MKLocalSearchCompleterDelegate {
    private let completer: MKLocalSearchCompleter
    var completions = [SearchResult]()

    init(completer: MKLocalSearchCompleter) {
        self.completer = completer
        super.init()
        self.completer.delegate = self
    }

    func update(queryFragment: String) {
        completer.resultTypes = .pointOfInterest
        completer.queryFragment = queryFragment
    }

    /*
     Run through the natural lang search results and add them along w location to newCompletions as a search result
     */
    func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        let group = DispatchGroup()
        var newCompletions = [SearchResult]()
        
        for result in completer.results {
            group.enter()
            let searchRequest = MKLocalSearch.Request()
            searchRequest.naturalLanguageQuery = result.title
            let search = MKLocalSearch(request: searchRequest)
            search.start { response, error in
                if let response = response, let mapItem = response.mapItems.first {
                    let coordinate = mapItem.placemark.coordinate
                    let searchResult = SearchResult(title: result.title, subTitle: result.subtitle, loc: coordinate)
                    newCompletions.append(searchResult)
                }
                group.leave()
            }
        }
        
        group.notify(queue: .main) { //once all locations found, update completion list
            self.completions = newCompletions
        }
    }
    
    func search(with query: String, coordinate: CLLocationCoordinate2D? = nil) async throws -> [SearchResult] {
        let mapKitRequest = MKLocalSearch.Request()
        mapKitRequest.naturalLanguageQuery = query
        mapKitRequest.resultTypes = .pointOfInterest
        if let coordinate {
            let origin = MKMapPoint(coordinate)
            let size = MKMapSize(width: 1, height: 1)
            let mapRect = MKMapRect(origin: origin, size: size)
            mapKitRequest.region = MKCoordinateRegion(mapRect)
        }
        let search = MKLocalSearch(request: mapKitRequest)

        let response = try await search.start()

        return response.mapItems.compactMap { mapItem in
            guard let loc = mapItem.placemark.location?.coordinate else { return SearchResult(title: "", subTitle: "", loc: CLLocationCoordinate2D(latitude: 0, longitude: 0)) }

            return SearchResult(title: mapItem.name ?? "", subTitle: mapItem.placemark.title ?? "", loc: loc)
        }
    }
}
