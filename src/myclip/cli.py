import argparse
import sys
from pathlib import Path

from myclip.config import DB_PATH, FAISS_PATH
from myclip.database import Database
from myclip.search import SearchIndex, hybrid_search
from myclip.ingest import ingest_directory
from myclip.export import export_clip
from myclip.config import EMBEDDING_DIM, CLIPS_DIR


def main():
    parser = argparse.ArgumentParser(description="MyClip — Scene-based video clipper")
    sub = parser.add_subparsers(dest="command")

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest episodes from a directory")
    p_ingest.add_argument("directory", help="Path to directory with video files")
    p_ingest.add_argument("--threshold", type=float, default=27.0)

    # search
    p_search = sub.add_parser("search", help="Search scenes by description")
    p_search.add_argument("query", help="Natural language description")
    p_search.add_argument("--season", type=int)
    p_search.add_argument("--limit", type=int, default=10)

    # list
    p_list = sub.add_parser("list", help="List scenes from an episode")
    p_list.add_argument("episode", help="Episode label (e.g., S01E03)")
    p_list.add_argument("--json", action="store_true")

    # export
    p_export = sub.add_parser("export", help="Export scenes as clips")
    p_export.add_argument("episode", help="Episode label")
    p_export.add_argument("scenes", help="Comma-separated scene numbers")

    # serve
    p_serve = sub.add_parser("serve", help="Start web UI")
    p_serve.add_argument("--port", type=int, default=8501)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    db = Database(DB_PATH)
    index = SearchIndex(dim=EMBEDDING_DIM, path=FAISS_PATH)

    if args.command == "ingest":
        count = ingest_directory(args.directory, db, index, threshold=args.threshold)
        print(f"Done. {count} scenes indexed.")

    elif args.command == "search":
        results = hybrid_search(args.query, index, db, k=args.limit)
        for scene in results:
            match_icon = {"visual+text": "[V+T]", "visual": "[V]", "text": "[T]"}.get(
                scene.get("match_type", ""), "[?]"
            )
            print(f"{match_icon} [{scene['score']:.3f}] {scene['episode']} "
                  f"scene {scene['scene_number']} "
                  f"({scene['start_time']:.1f}s-{scene['end_time']:.1f}s)")
            print(f"  {scene['subtitle_text'][:80]}")
            print()

    elif args.command == "list":
        scenes = db.get_scenes(episode=args.episode)
        for s in scenes:
            print(f"Scene {s['scene_number']}: {s['start_time']:.1f}s - {s['end_time']:.1f}s")
            print(f"  {s['subtitle_text'][:80]}")

    elif args.command == "export":
        scene_nums = [int(x.strip()) for x in args.scenes.split(",")]
        scenes = db.get_scenes(episode=args.episode)
        for s in scenes:
            if s["scene_number"] in scene_nums:
                out = CLIPS_DIR / f"{args.episode}_scene{s['scene_number']}.mp4"
                export_clip(s["video_path"], s["start_time"], s["end_time"], out)
                print(f"Exported: {out}")

    elif args.command == "serve":
        import uvicorn
        from myclip.api import create_app
        app = create_app(db, index)
        uvicorn.run(app, port=args.port)

    db.close()


if __name__ == "__main__":
    main()
