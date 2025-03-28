from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
import os
import time
import pygame

# 初始化 MCP 服务器
mcp = FastMCP("LocalMusicPlayerServer")

# 初始化 pygame 音频模块
pygame.mixer.init()

# 音乐播放器状态
class MusicPlayer:
    def __init__(self, music_dir: str = "music"):
        self.music_dir = music_dir
        self.playlist: List[Dict[str, str]] = []  # 播放列表，存储音乐信息
        self.current_index: Optional[int] = None   # 当前播放的音乐索引
        self.is_playing: bool = False             # 是否正在播放
        self.start_time: Optional[float] = None   # 开始播放的时间
        self.load_playlist()                      # 加载音乐目录下的文件

    def load_playlist(self) -> None:
        """
        加载 music 目录下的音乐文件到播放列表。
        """
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir, exist_ok=True)
            return

        supported_formats = (".mp3", ".wav", ".ogg", ".flac")
        for file in os.listdir(self.music_dir):
            if file.lower().endswith(supported_formats):
                music_path = os.path.join(self.music_dir, file)
                music_name = os.path.splitext(file)[0]
                self.playlist.append({
                    "name": music_name,
                    "path": music_path,
                    "duration": "00:00"  # 可以扩展为读取实际时长
                })

    def play(self, index: int) -> Dict[str, str]:
        """
        播放指定索引的音乐。

        params:
            index: 音乐索引

        return:
            返回当前播放的音乐信息
        """
        if index < 0 or index >= len(self.playlist):
            return {"error": "Invalid index"}

        music = self.playlist[index]
        try:
            pygame.mixer.music.load(music["path"])
            pygame.mixer.music.play()
            self.current_index = index
            self.is_playing = True
            self.start_time = time.time()
            return music
        except Exception as e:
            return {"error": f"Failed to play music: {e}"}

    def pause(self) -> Dict[str, str]:
        """
        暂停当前播放的音乐。

        return:
            返回当前播放的音乐信息
        """
        if not self.is_playing or self.current_index is None:
            return {"error": "No music is playing"}

        pygame.mixer.music.pause()
        self.is_playing = False
        return self.playlist[self.current_index]

    def unpause(self) -> Dict[str, str]:
        """
        继续播放当前音乐。

        return:
            返回当前播放的音乐信息
        """
        if self.current_index is None:
            return {"error": "No music is selected"}

        pygame.mixer.music.unpause()
        self.is_playing = True
        return self.playlist[self.current_index]

    def stop(self) -> Dict[str, str]:
        """
        停止当前播放的音乐。

        return:
            返回停止的音乐信息
        """
        if not self.is_playing or self.current_index is None:
            return {"error": "No music is playing"}

        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_index = None
        self.start_time = None
        return {"status": "stopped"}

    def get_status(self) -> Dict[str, str]:
        """
        获取当前播放状态。

        return:
            返回播放状态信息
        """
        if self.current_index is None:
            return {"status": "idle"}

        current_music = self.playlist[self.current_index]
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            "status": "playing" if self.is_playing else "paused",
            "current_music": current_music,
            "elapsed_time": f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
        }

    def get_playlist(self) -> List[Dict[str, str]]:
        """
        获取播放列表。

        return:
            返回播放列表
        """
        return self.playlist

# 初始化音乐播放器
player = MusicPlayer()

@mcp.tool()
def play_music(index: int) -> Dict[str, str]:
    """
    播放指定索引的音乐。

    params:
        index: 音乐索引

    return:
        返回当前播放的音乐信息
    """
    return player.play(index-1)

@mcp.tool()
def pause_music() -> Dict[str, str]:
    """
    暂停当前播放的音乐。

    return:
        返回当前播放的音乐信息
    """
    return player.pause()

@mcp.tool()
def unpause_music() -> Dict[str, str]:
    """
    继续播放当前音乐。

    return:
        返回当前播放的音乐信息
    """
    return player.unpause()

@mcp.tool()
def stop_music() -> Dict[str, str]:
    """
    停止当前播放的音乐。

    return:
        返回停止的音乐信息
    """
    return player.stop()

@mcp.tool()
def get_playlist() -> List[Dict[str, str]]:
    """
    获取播放列表。

    return:
        返回播放列表
    """
    return player.get_playlist()

@mcp.tool()
def get_status() -> Dict[str, str]:
    """
    获取当前播放状态。

    return:
        返回播放状态信息
    """
    return player.get_status()

# 启动服务器
if __name__ == "__main__":
    mcp.run()