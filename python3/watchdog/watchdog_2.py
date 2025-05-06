# coding: utf-8

import sys
import time
import os
import argparse
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import logging

# Configuración mejorada de logging
def setup_logging(log_level=logging.INFO, log_file=None):
    """Configure logging with proper format and optional file output."""
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    handlers.append(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


class EnhancedEventHandler(PatternMatchingEventHandler):
    """Enhanced event handler with detailed event processing."""
    
    def __init__(self, patterns=None, ignore_patterns=None, 
                 ignore_directories=False, case_sensitive=True):
        super().__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns, 
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive
        )
        self.event_count = 0
    
    def on_any_event(self, event):
        """Handle any file system event."""
        self.event_count += 1
        logging.info(f"Event #{self.event_count}: {event.event_type} - {event.src_path}")
    
    def on_created(self, event):
        """Handle file/directory creation event."""
        logging.debug(f"Created: {event.src_path}")
        if not event.is_directory:
            file_size = os.path.getsize(event.src_path)
            logging.info(f"New file created: {event.src_path} ({file_size} bytes)")
    
    def on_deleted(self, event):
        """Handle file/directory deletion event."""
        logging.debug(f"Deleted: {event.src_path}")
    
    def on_modified(self, event):
        """Handle file/directory modification event."""
        logging.debug(f"Modified: {event.src_path}")
        if not event.is_directory:
            file_size = os.path.getsize(event.src_path)
            logging.info(f"File modified: {event.src_path} ({file_size} bytes)")
    
    def on_moved(self, event):
        """Handle file/directory move event."""
        logging.debug(f"Moved: {event.src_path} -> {event.dest_path}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Monitor file system events with pattern matching')
    
    parser.add_argument('path', nargs='?', default=os.getcwd(),
                        help='Directory path to monitor (default: current directory)')
    
    parser.add_argument('-p', '--patterns', nargs='+', default=['*.py', '*.pyc'],
                        help='File patterns to watch (default: *.py *.pyc)')
    
    parser.add_argument('-i', '--ignore-patterns', nargs='+', default=['version.py'],
                        help='File patterns to ignore (default: version.py)')
    
    parser.add_argument('-d', '--ignore-directories', action='store_true',
                        help='Ignore directory events')
    
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                        help='Monitor directories recursively')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging (DEBUG level)')
    
    parser.add_argument('-l', '--log-file',
                        help='Log to file instead of console')
    
    return parser.parse_args()


def main():
    """Main function to run the file system monitor."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level, args.log_file)
    
    # Normalize and validate path
    path = Path(args.path).resolve()
    if not path.exists():
        logging.error(f"Path does not exist: {path}")
        return 1
    
    logging.info(f"Starting file system monitor on: {path}")
    logging.info(f"Watching patterns: {args.patterns}")
    logging.info(f"Ignoring patterns: {args.ignore_patterns}")
    
    # Create event handler
    event_handler = EnhancedEventHandler(
        patterns=args.patterns,
        ignore_patterns=args.ignore_patterns,
        ignore_directories=args.ignore_directories
    )
    
    # Setup and start observer
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=args.recursive)
    observer.start()
    
    try:
        logging.info("Observer started. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping observer (Ctrl+C pressed)...")
    finally:
        observer.stop()
        observer.join()
        logging.info(f"Monitoring stopped. Processed {event_handler.event_count} events.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())