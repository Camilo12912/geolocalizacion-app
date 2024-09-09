import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy_garden.mapview import MapView, MapMarker, MapMarkerPopup

# Clase personalizada para elementos de la lista con efecto hover
class HoverBehavior(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_color = (0, 0, 0, 0.1)
        self.hover_color = (0.9, 0.9, 0.9, 1)  # Color más claro al hacer hover

        with self.canvas.before:
            self.bg_color = Color(*self.original_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.bind(pos=self.update_bg_rect, size=self.update_bg_rect)

    def update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_enter(self):
        self.bg_color.rgba = self.hover_color

    def on_leave(self):
        self.bg_color.rgba = self.original_color

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [20, 50, 20, 20]
        self.spacing = 20

        # Lista para almacenar los marcadores
        self.markers = []

        # Fondo de la aplicación
        with self.canvas.before:
            Color(0.992, 0.965, 0.89, 1)  # Color de fondo #fdf6e3
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)

        # Título
        self.title_label = Label(
            text="Busca lugares cercanos",
            font_size=32,
            bold=True,
            size_hint=(1, None),
            height=50,
            color=(0.1, 0.1, 0.1, 1)  # Color del texto
        )
        self.add_widget(self.title_label)

        # Contenedor para el Spinner y el botón
        controls_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        # Spinner (menú desplegable)
        self.place_type_spinner = Spinner(
            text='Lugares turísticos',
            values=('Lugares turísticos', 'Hoteles', 'Restaurantes'),
            size_hint=(1, None),
            height=50,
            color=(0, 0, 0, 1),  # Color del texto en el Spinner
            background_color=(0.8, 0.8, 0.8, 1),  # Color del fondo del Spinner #ccc
            background_normal=''
        )
        with self.place_type_spinner.canvas.before:
            Color(0.8, 0.8, 0.8, 1)  # Color del fondo del Spinner
            self.spinner_rect = RoundedRectangle(pos=self.place_type_spinner.pos, size=self.place_type_spinner.size, radius=[20])
            self.place_type_spinner.bind(pos=self.update_spinner_rect, size=self.update_spinner_rect)
        controls_layout.add_widget(self.place_type_spinner)

        # Botón de búsqueda
        self.search_button = Button(
            text="Buscar",
            size_hint=(0.3, None),
            height=50,
            color=(1, 1, 1, 1),  # Color del texto (blanco)
            background_color=(0.361, 0.725, 0.361, 1),  # Color del botón #5cb85c
            background_normal=''
        )
        with self.search_button.canvas.before:
            Color(0.361, 0.725, 0.361, 1)  # Fondo del botón
            self.button_rect = RoundedRectangle(pos=self.search_button.pos, size=self.search_button.size, radius=[20])
            self.search_button.bind(pos=self.update_button_rect, size=self.update_button_rect)
        self.search_button.bind(on_press=self.search_places)
        controls_layout.add_widget(self.search_button)

        self.add_widget(controls_layout)

        # Inicializar la ubicación simulada
        self.simulated_location = (7.900412097203202, -72.50295964581814)  # Coordenadas de ejemplo

        # Agregar el mapa
        self.map_view = MapView(
            zoom=12,
            lat=self.simulated_location[0],
            lon=self.simulated_location[1],
            size_hint=(1, 4)  # Ajusta el tamaño del mapa aquí
        )
        self.add_widget(self.map_view)

        # Agregar el marcador personalizado en la ubicación simulada
        self.custom_marker = MapMarkerPopup(
            lat=self.simulated_location[0],
            lon=self.simulated_location[1],
            source="custom_marker.png",  # Asegúrate de tener esta imagen en tu directorio de proyecto
            size=(5, 5)
        )
        self.map_view.add_widget(self.custom_marker)

        # Contenedor desplazable para la lista de lugares
        self.places_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.places_list.bind(minimum_height=self.places_list.setter('height'))

        scroll_view = ScrollView(size_hint=(1, None), height=300)
        scroll_view.add_widget(self.places_list)
        self.add_widget(scroll_view)

        self.search_places(None)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_spinner_rect(self, *args):
        self.spinner_rect.pos = self.place_type_spinner.pos
        self.spinner_rect.size = self.place_type_spinner.size

    def update_button_rect(self, *args):
        self.button_rect.pos = self.search_button.pos
        self.button_rect.size = self.search_button.size

    def search_places(self, instance):
        place_type = self.place_type_spinner.text.lower()
        location = self.simulated_location  # Usa la ubicación simulada

        if place_type == 'lugares turísticos':
            query_tag = 'tourism="attraction"'
        elif place_type == 'hoteles':
            query_tag = 'tourism="hotel"'
        elif place_type == 'restaurantes':
            query_tag = 'amenity="restaurant"'
        else:
            query_tag = 'tourism="attraction"'  # Valor por defecto

        if location:
            latitude, longitude = location
            # Consultar la API de Overpass para obtener lugares cercanos
            query = f"""
            [out:json];
            node
            [{query_tag}]
            (around:1000,{latitude},{longitude});
            out body;
            """
            url = "http://overpass-api.de/api/interpreter"
            try:
                response = requests.get(url, params={'data': query})
                response.raise_for_status()
                data = response.json()

                print('Datos:', data)  # Verifica el contenido de la respuesta
                
                self.places_list.clear_widgets()

                # Eliminar los marcadores antiguos
                for marker in self.markers:
                    self.map_view.remove_widget(marker)
                self.markers.clear()

                if 'elements' in data and data['elements']:
                    # Lista de ubicaciones para centrar el mapa
                    locations = []
                    
                    for element in data['elements']:
                        tags = element.get('tags', {})
                        place_name = tags.get('name', 'Sin nombre')
                        lat = element['lat']
                        lon = element['lon']
                        
                        # Crear un elemento de lista con efecto hover
                        place_item = HoverBehavior(
                            text=place_name, 
                            size_hint_y=None, 
                            height=50, 
                            color=(0, 0, 0, 1)
                        )
                        self.places_list.add_widget(place_item)
                        
                        # Agregar ubicaciones para centrar el mapa
                        locations.append((lat, lon))
                        
                        # Crear y agregar un marcador al mapa
                        marker = MapMarker(lat=lat, lon=lon)
                        self.map_view.add_widget(marker)
                        self.markers.append(marker)  # Agregar el marcador a la lista
                        
                    if locations:
                        # Centrar el mapa en el primer lugar encontrado
                        first_location = locations[0]
                        self.map_view.center_on(*first_location)
                        self.map_view.zoom = 16  # Ajusta el nivel de zoom según sea necesario
                        
                else:
                    # Mostrar mensaje cuando no se encuentran lugares
                    no_data_label = Label(
                        text="No se encontraron lugares", 
                        size_hint_y=None, 
                        height=40, 
                        color=(0, 0, 0, 1)  # Color negro
                    )
                    self.places_list.add_widget(no_data_label)

            except requests.RequestException as e:
                print(f'Error al hacer la solicitud: {e}')
        else:
            self.title_label.text = "Could not get current location."

class TouristPlacesApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    TouristPlacesApp().run()
