"""Cache layer for GTFS static data."""

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from sofiaclient.exceptions import CacheError, EfaConnectionError


class GTFSCache:
    """Manages caching of GTFS static data with TTL."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        ttl_hours: int = 24,
    ) -> None:
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache files (default: ~/.cache/sofiaclient)
            ttl_hours: Time-to-live for cached data in hours
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "sofiaclient"
        
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, url: str) -> Path:
        """Get cache file path for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"gtfs_static_{url_hash}.zip"

    def get_metadata_path(self, cache_path: Path) -> Path:
        """Get metadata file path for a cache file."""
        return cache_path.with_suffix(".meta")

    async def get_static_data(self, url: str) -> Path:
        """
        Get static GTFS data, using cache if valid.
        
        Args:
            url: URL to static GTFS ZIP file
            
        Returns:
            Path to cached GTFS ZIP file
        """
        cache_path = self.get_cache_path(url)
        metadata_path = self.get_metadata_path(cache_path)

        # Check if cache exists and is valid
        if cache_path.exists() and metadata_path.exists():
            if await self._is_cache_valid(cache_path, metadata_path, url):
                return cache_path

        # Download fresh data
        return await self._download_static_gtfs(url, cache_path, metadata_path)

    async def _is_cache_valid(
        self, cache_path: Path, metadata_path: Path, url: str
    ) -> bool:
        """Check if cached data is still valid."""
        try:
            # Check age-based TTL
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age > self.ttl:
                return False

            # Check remote Last-Modified header
            metadata = self._read_metadata(metadata_path)
            last_modified = metadata.get("last_modified")

            if last_modified:
                remote_modified = await self._get_remote_last_modified(url)
                if remote_modified and remote_modified != last_modified:
                    return False

            return True
        except (OSError, ValueError):
            return False

    async def _get_remote_last_modified(self, url: str) -> str | None:
        """Get Last-Modified header from remote server."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(url, follow_redirects=True)
                return response.headers.get("Last-Modified")
        except httpx.HTTPError:
            return None

    async def _download_static_gtfs(
        self, url: str, cache_path: Path, metadata_path: Path
    ) -> Path:
        """Download static GTFS data and cache it."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Write data to cache
                cache_path.write_bytes(response.content)

                # Write metadata
                metadata = {
                    "url": url,
                    "last_modified": response.headers.get("Last-Modified"),
                    "etag": response.headers.get("ETag"),
                    "downloaded_at": datetime.now().isoformat(),
                }
                self._write_metadata(metadata_path, metadata)

                return cache_path

        except httpx.HTTPError as e:
            raise EfaConnectionError(f"Failed to download static GTFS data: {e}") from e
        except OSError as e:
            raise CacheError(f"Failed to write cache file: {e}") from e

    def _read_metadata(self, metadata_path: Path) -> dict[str, Any]:
        """Read metadata from file."""
        import json
        
        try:
            return json.loads(metadata_path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_metadata(self, metadata_path: Path, metadata: dict[str, Any]) -> None:
        """Write metadata to file."""
        import json
        
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def clear_cache(self) -> None:
        """Clear all cached files."""
        for file in self.cache_dir.glob("gtfs_static_*.zip"):
            file.unlink(missing_ok=True)
        for file in self.cache_dir.glob("gtfs_static_*.meta"):
            file.unlink(missing_ok=True)

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about cached files."""
        files = list(self.cache_dir.glob("gtfs_static_*.zip"))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "num_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
