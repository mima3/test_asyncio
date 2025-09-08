from __future__ import annotations
import sys
import threading
import weakref
from types import FrameType
from datetime import datetime
from dataclasses import dataclass
import time


_prev_sys_profile = None
_prev_thr_profile = None
# WeakKeyDictionaryなので、オブジェクトが消えたらsetから消える
# オブジェクトが生存している間、id()は再利用される可能性があるが消えているはずなので
# 生存期間については一意がたもてる
_seen_threads = weakref.WeakSet()

# スレッドごとのローカル変数
# インスタンスごとに独立した空間なので、別のインスタンスで同名の変数があっても干渉はしない
_tls = threading.local()


@dataclass
class ThreadData:
    start_time: datetime
    end_time: datetime
    name: str
    ident: int | None
    line_no: int
    file_name: str


_dict_thread_info: dict[int, ThreadData] = {}
_next_thread_info_id = 1
_install_time = 0.0


def install_profile_hooks() -> None:
    """
    setprofile を使って全スレッド（_thread 由来も含む）の開始/終了を“できるだけ”検知。
    ※ Python バイトコードを一度も実行しないまま終わるスレッドは検知不可。
    """
    global _prev_sys_profile, _prev_thr_profile
    global _install_time
    _install_time = time.perf_counter()

    def on_start(t: threading.Thread, frame: FrameType):
        global _next_thread_info_id
        start = datetime.now()
        info = ThreadData(
            start_time=start,
            end_time=start,
            name=t.name,
            ident=t.ident,
            file_name=frame.f_code.co_filename,
            line_no=frame.f_lineno,
        )
        _dict_thread_info[_next_thread_info_id] = info
        _tls.next_thread_info_id = _next_thread_info_id
        _next_thread_info_id += 1

    def on_end(t: threading.Thread):
        # print(f"[THREAD END] {_tls.thread_name} ident={t.ident}")
        if hasattr(_tls, "next_thread_info_id"):
            _dict_thread_info[_tls.next_thread_info_id].end_time = datetime.now()

    _prev_sys_profile = sys.getprofile()
    _prev_thr_profile = threading.getprofile()

    def prof(frame: FrameType, event: str, arg):
        # 初回イベントで bottom フレームを特定し、開始通知
        if not hasattr(_tls, "bottom_id"):
            # スタックの一番下の Python フレームを求める
            bottom = frame
            while bottom and bottom.f_back:
                bottom = bottom.f_back
            _tls.bottom_id = id(bottom) if bottom else None

            th = threading.current_thread()
            if th not in _seen_threads:
                _seen_threads.add(th)
                try:
                    on_start(th, frame)
                except Exception as e:
                    print(e)
                    pass

        # “最下層フレーム”が return したら終了通知
        if event == "return" and getattr(_tls, "bottom_id", None) == id(frame):
            try:
                on_end(threading.current_thread())
            finally:
                # このスレッドだけプロファイルを外してオーバーヘッド削減（任意）
                sys.setprofile(None)

        # 既存のプロファイラがあればチェーン
        if _prev_sys_profile:
            _prev_sys_profile(frame, event, arg)

    sys.setprofile(prof)  # 現在スレッド
    threading.setprofile(prof)  # 今後起動するスレッドすべてに配布


def uninstall_profile_hooks() -> None:
    global _prev_sys_profile, _prev_thr_profile
    sys.setprofile(_prev_sys_profile)
    threading.setprofile(_prev_thr_profile)
    _prev_sys_profile = _prev_thr_profile = None
    print("スレッドの生成状況 ==============")
    # MainThread(動作中)は終了時間が記録されないので時間は取得できない
    # Thread-1 (_do_shutdown) はshutdown_default_executorでexecutorが終了するまでまつためのスレッド
    # https://github.com/python/cpython/blob/b0420b505e6c9bbc8418e0f6240835ea777137b5/Lib/asyncio/base_events.py#L606
    for v in sorted(_dict_thread_info.values(), key=lambda x: x.start_time):
        time_delta = "時間取得できない"
        if v.end_time != v.start_time:
            time_delta = v.end_time - v.start_time
        print(v.name, v.start_time, time_delta)
    print(f"done in {time.perf_counter() - _install_time:.3f}s")
