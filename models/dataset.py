# models/dataset.py

class Dataset:
    """
    Represents a dataset in the Multi-Domain Intelligence Platform.
    This maps directly to the 'datasets_metadata' table.
    """

    def __init__(
        self,
        dataset_id: int,
        name: str,
        category: str,
        source: str,
        last_updated: str,
        record_count: int,
        file_size_mb: float,
    ) -> None:
        self.__id = dataset_id
        self.__name = name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb

    # --- Getters (simple, clear for a first–year project) ---

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_category(self) -> str:
        return self.__category

    def get_source(self) -> str:
        return self.__source

    def get_last_updated(self) -> str:
        return self.__last_updated

    def get_record_count(self) -> int:
        return self.__record_count

    def get_file_size_mb(self) -> float:
        return self.__file_size_mb

    # --- Simple helper methods ---

    def is_large_dataset(self, threshold_mb: float = 100.0) -> bool:
        """Return True if the dataset is considered large."""
        return self.__file_size_mb >= threshold_mb

    def to_dict(self) -> dict:
        """Convert this object into a dictionary for easy DataFrame creation."""
        return {
            "id": self.__id,
            "dataset_name": self.__name,
            "category": self.__category,
            "source": self.__source,
            "last_updated": self.__last_updated,
            "record_count": self.__record_count,
            "file_size_mb": self.__file_size_mb,
        }

    def __str__(self) -> str:
        return (
            f"Dataset {self.__id}: {self.__name} "
            f"({self.__category}, {self.__record_count} records, {self.__file_size_mb:.2f} MB)"
        )
