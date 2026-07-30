import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.requirements_service import RequirementsService

async def main():
    service = RequirementsService()
    idea = "Trailhead: A healthcare platform where patients can book doctor appointments, manage medical records, receive appointment reminders, and find the right specialists."
    print("Sending request to Ollama...")
    try:
        res = await service.generate_requirements(idea)
        print("Success!")
        print(res.model_dump_json(indent=2))
    except Exception as e:
        print("Error encountered:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
