# Fetch HLS Stream

```bash
python -m fetch_hls_stream --url M3U8_URL --output . --freq 10
```

In the case of VOH 95.6MHz, the M3U8_URL is `https://strm.voh.com.vn/radio/channel1/playlist.m3u8`

To join the audio files.

```bash
python join_auto_files.py
```
