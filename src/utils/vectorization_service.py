from sentence_transformers import SentenceTransformer

class VectorizationService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the vectorization service with a specified model."""
        self.model = SentenceTransformer(model_name)

    def vectorize_text(self, text):
        """
        Vectorize the given text.

        Args:
            text (str): The text to vectorize.

        Returns:
            list: A list representing the vectorized text (embedding).
        """
        if text:
            # Get vector directly from the model (will be 384 dimensions)
            vector = self.model.encode(text)  # This returns a numpy array
            return vector.tolist()  # Convert numpy array to list for easier handling
        else:
            return None  # Return None if the input text is empty
