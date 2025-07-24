#!/usr/bin/env python3
"""
Collectibles CLI

Unified command-line interface for managing multiple collectibles archives.
Supports forums, auction houses, and content sites.
"""
import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.scrapers.forums import Net54Scraper
from tools.scrapers.auctions import HeritageScraper
from tools.scrapers.base.storage import MultiArchiveStorage


class CollectiblesCLI:
    """Main CLI for collectibles repository"""
    
    def __init__(self):
        self.scrapers = {
            'net54': Net54Scraper,
            'heritage': HeritageScraper,
            # Add more scrapers as they're implemented
            # 'psa': PSAScraper,
            # 'prewarcards': PrewarCardsScraper,
        }
    
    def list_archives(self):
        """List all available archives"""
        print("\n📚 Available Archives:\n")
        
        # Check configured archives
        configs_dir = Path('configs')
        if configs_dir.exists():
            for config_file in configs_dir.glob('*.yaml'):
                archive_name = config_file.stem
                print(f"  • {archive_name}")
                
                # Show stats if data exists
                for archive_type in ['forums', 'auctions', 'content']:
                    data_path = Path(f'archives/{archive_type}/{archive_name}/data')
                    if data_path.exists():
                        storage = MultiArchiveStorage(archive_name, 'archives')
                        stats = storage.get_stats()
                        print(f"    Type: {archive_type}")
                        print(f"    Items: {stats['total_items']}")
                        print(f"    Size: {stats['total_size_mb']} MB")
                        print(f"    Last update: {stats['last_update']}")
                        break
                print()
    
    def scrape_archive(self, archive: str, **kwargs):
        """Scrape a specific archive
        
        Args:
            archive: Name of archive to scrape
            **kwargs: Additional arguments for scraper
        """
        if archive not in self.scrapers:
            print(f"❌ Unknown archive: {archive}")
            print(f"   Available: {', '.join(self.scrapers.keys())}")
            return
        
        print(f"\n🔄 Starting {archive} scraper...\n")
        
        # Initialize and run scraper
        scraper_class = self.scrapers[archive]
        config_path = f'configs/{archive}.yaml'
        
        if not Path(config_path).exists():
            print(f"❌ Configuration not found: {config_path}")
            return
        
        try:
            scraper = scraper_class(config_path)
            
            # Pass archive-specific arguments
            if archive == 'net54':
                scraper.scrape(
                    forum_id=kwargs.get('forum_id'),
                    thread_limit=kwargs.get('limit')
                )
            elif archive == 'heritage':
                scraper.scrape(
                    auction_id=kwargs.get('auction_id'),
                    lot_limit=kwargs.get('limit')
                )
            else:
                scraper.scrape()
                
        except KeyboardInterrupt:
            print("\n⚠️  Scraping interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_stats(self, archive: Optional[str] = None):
        """Show statistics for archives
        
        Args:
            archive: Specific archive to show stats for (optional)
        """
        print("\n📊 Archive Statistics\n")
        
        if archive:
            archives = [archive]
        else:
            # Find all archives with data
            archives = []
            for archive_type in ['forums', 'auctions', 'content']:
                type_dir = Path(f'archives/{archive_type}')
                if type_dir.exists():
                    for archive_dir in type_dir.iterdir():
                        if archive_dir.is_dir() and (archive_dir / 'data').exists():
                            archives.append(archive_dir.name)
        
        total_items = 0
        total_size = 0
        
        for archive_name in archives:
            try:
                storage = MultiArchiveStorage(archive_name, 'archives')
                stats = storage.get_stats()
                
                print(f"📁 {archive_name}")
                print(f"   Type: {stats['archive_type']}")
                print(f"   Total items: {stats['total_items']:,}")
                print(f"   Total size: {stats['total_size_mb']:.2f} MB")
                print(f"   Last update: {stats['last_update'] or 'Never'}")
                
                if stats['items_by_type']:
                    print("   Items by type:")
                    for item_type, count in stats['items_by_type'].items():
                        print(f"     - {item_type}: {count:,}")
                
                print()
                
                total_items += stats['total_items']
                total_size += stats['total_size_mb']
                
            except Exception as e:
                print(f"   ⚠️  Error reading stats: {e}\n")
        
        if len(archives) > 1:
            print(f"📈 Total across all archives:")
            print(f"   Items: {total_items:,}")
            print(f"   Size: {total_size:.2f} MB")
    
    def export_metadata(self, archive: str, output_path: Optional[str] = None):
        """Export metadata for an archive
        
        Args:
            archive: Archive to export
            output_path: Optional output path
        """
        try:
            storage = MultiArchiveStorage(archive, 'archives')
            output_file = storage.export_metadata(
                Path(output_path) if output_path else None
            )
            print(f"✅ Metadata exported to: {output_file}")
        except Exception as e:
            print(f"❌ Error exporting metadata: {e}")
    
    def verify_setup(self):
        """Verify the collectibles setup"""
        print("\n🔍 Verifying Collectibles Setup\n")
        
        checks = {
            'Directory structure': Path('archives').exists(),
            'Configurations': Path('configs').exists() and any(Path('configs').glob('*.yaml')),
            'Base scraper': Path('tools/scrapers/base/base_scraper.py').exists(),
            'Storage system': Path('tools/scrapers/base/storage.py').exists(),
            'Net54 scraper': Path('tools/scrapers/forums/net54_scraper.py').exists(),
        }
        
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n✅ All systems ready!")
        else:
            print("\n⚠️  Some components missing. Run migration first.")
        
        return all_good


def main():
    parser = argparse.ArgumentParser(
        description='Collectibles Archive Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  collectibles.py list                    # List all archives
  collectibles.py scrape net54 --forum 39 # Scrape Net54 forum
  collectibles.py scrape heritage         # Scrape Heritage auctions
  collectibles.py stats                   # Show all statistics
  collectibles.py stats net54            # Show Net54 statistics
  collectibles.py verify                  # Verify setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    subparsers.add_parser('list', help='List available archives')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape an archive')
    scrape_parser.add_argument('archive', help='Archive to scrape (e.g., net54, heritage)')
    scrape_parser.add_argument('--forum', '--forum-id', type=int, dest='forum_id',
                              help='Forum ID for forum scrapers')
    scrape_parser.add_argument('--auction', '--auction-id', dest='auction_id',
                              help='Auction ID for auction scrapers')
    scrape_parser.add_argument('--limit', type=int,
                              help='Limit number of items to scrape')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show archive statistics')
    stats_parser.add_argument('archive', nargs='?', help='Specific archive (optional)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export archive metadata')
    export_parser.add_argument('archive', help='Archive to export')
    export_parser.add_argument('--output', '-o', help='Output file path')
    
    # Verify command
    subparsers.add_parser('verify', help='Verify collectibles setup')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = CollectiblesCLI()
    
    # Execute command
    if args.command == 'list':
        cli.list_archives()
    elif args.command == 'scrape':
        cli.scrape_archive(
            args.archive,
            forum_id=getattr(args, 'forum_id', None),
            auction_id=getattr(args, 'auction_id', None),
            limit=getattr(args, 'limit', None)
        )
    elif args.command == 'stats':
        cli.show_stats(args.archive)
    elif args.command == 'export':
        cli.export_metadata(args.archive, args.output)
    elif args.command == 'verify':
        cli.verify_setup()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()