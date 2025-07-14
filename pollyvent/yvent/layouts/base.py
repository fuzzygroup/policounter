# pollyvent/yvent/layouts/base.py

from abc import ABC, abstractmethod

class Layout(ABC):
    """
    Abstract base class for flyer layouts.
    Subclasses must implement the render() method to define visual placement.
    """

    @abstractmethod
    def render(self, composer, data):
        """
        Render the layout using an ImageComposer and event data.

        Parameters:
        - composer: An instance of ImageComposer with canvas and drawing methods
        - data: A dictionary containing keys like:
            - 'title': str
            - 'datetime': datetime.datetime
            - 'location': str
            - 'qr_text': str or None
            - 'logo_path': Path or str
            - 'font_path': Path or str
            - 'output_path': Path or str
        """
        pass

    def validate_data(self, data):
        """
        Optional helper to check if all required fields are present.
        Can be overridden or extended in subclasses.
        """
        required_keys = ['title', 'datetime', 'location', 'logo_path', 'font_path']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required field in layout data: '{key}'")

