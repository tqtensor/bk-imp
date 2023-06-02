# TTSLab

## ffmpeg

```bash
# Set the download URL
download_url="https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz"

# Set the installation directory
installation_dir="$HOME/ffmpeg"

# Create the installation directory if it doesn't exist
mkdir -p "$installation_dir"

# Download the ffmpeg static build archive
echo "Downloading ffmpeg..."
wget "$download_url" -O ffmpeg.tar.xz

# Extract the archive to the installation directory
echo "Extracting ffmpeg..."
tar -xf ffmpeg.tar.xz -C "$installation_dir" --strip-components=1

# Clean up the downloaded archive
echo "Cleaning up..."
rm ffmpeg.tar.xz

echo "ffmpeg has been installed to: $installation_dir"
```
