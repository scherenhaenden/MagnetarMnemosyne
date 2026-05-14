import os

from config import get_audio_setting


generated_audio_dir = get_audio_setting("audio", "paths", "generated_audio_dir", default="src/generated_audio")
if not os.path.isabs(generated_audio_dir):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    generated_audio_dir = os.path.join(project_root, generated_audio_dir)
os.makedirs(generated_audio_dir, exist_ok=True)


def public_audio_url(local_path: str) -> str:
    if not local_path:
        return ""
    absolute_local_path = os.path.abspath(local_path)
    absolute_generated_dir = os.path.abspath(generated_audio_dir)
    if absolute_local_path.startswith(absolute_generated_dir + os.sep) or absolute_local_path == absolute_generated_dir:
        relative_path = os.path.relpath(absolute_local_path, absolute_generated_dir)
        return f"/generated-audio/{relative_path.replace(os.sep, '/')}"
    return local_path
