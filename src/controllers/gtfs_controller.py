import threading
from typing import Any, Callable, Optional

try:
    from processor import GTFSProcessor
except ModuleNotFoundError:
    from src.processor import GTFSProcessor


class GTFSController:
    """Handles GTFS loading lifecycle and asynchronous processor creation."""

    def __init__(self, processor_factory: Callable[[str], Any] = GTFSProcessor):
        self.processor_factory = processor_factory

    def create_processor(self, file_path: str, old_processor: Optional[Any] = None) -> Any:
        """Closes old processor if available and creates a new processor instance."""
        if old_processor is not None:
            old_processor.close()
        return self.processor_factory(file_path)

    def load_async(
        self,
        file_path: str,
        old_processor: Optional[Any],
        on_loaded: Callable[[Any], None],
        on_error: Callable[[str], None],
    ) -> threading.Thread:
        """Loads GTFS in a background thread and triggers callbacks."""

        def _thread_load():
            try:
                processor = self.create_processor(file_path, old_processor)
                on_loaded(processor)
            except Exception as exc:
                on_error(str(exc))

        thread = threading.Thread(target=_thread_load, daemon=True)
        thread.start()
        return thread
