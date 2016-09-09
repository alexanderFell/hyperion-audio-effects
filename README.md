Hyperion audio effects
======================

##### Examples: https://www.youtube.com/watch?v=n-_0KG4EsY8 https://www.youtube.com/watch?v=HiAlv-mW9UI

Dev kit for creating audio visualizations for [hyperion](https://github.com/tvdzwan/hyperion).

- Update 27/3/2016: Config file (config.json), matrix configurator, protobuf support
- Update 8/4/2015: Some improvements and cleanup, new video
- Update 31/3/2015: New parameters and hyperion config file parsing

### Installation and running on Debian **

1. Install Gstreamer 1.0 and PyGI: `sudo apt-get install libgstreamer1.0-0 gir1.2-gstreamer-1.0 gir1.2-glib-2.0 gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-good gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-pulseaudio python-gi`
2. Install Tkinter for GUI: `sudo apt-get install python-tk`
3. Install pip: `sudo apt-get install python-pip`
4. Install dependencies: `sudo pip install -r requirements.txt` (or use virtualenv if you like)
5. Put `options snd-aloop index=-2` in end of `/etc/modprobe.d/alsa-base.conf` to prevent loopback device for getting first card index
6. Enable loopback device `modprobe snd-aloop` (and type line `snd-aloop` to /etc/modules to make it permanent)
7. Included are 2 different asound configuration files: `asound.conf.loopback` and `asound.conf.mic`. Choose `asound.conf.mic`, if you have a microphone attached to your raspberry pi through e.g. an external USB sound card. The sound levels recorded by the microphone will be used to create the effects. If you do not have a microphone, use `asound.conf.loopback` to utilize the loopback device.
8. Rename the chosen asound configuration file to  `.asoundrc` and copy it to your home folder (backup old if exists) and change the soundcard index if needed (`"hw:<card>,<device>"`, check `aplay -l`) *
9. Reboot or reload alsa `sudo alsa force-reload`
10. Run `python main.py` with options:
	- `--config=<path>` path to hyperion config file (defaults to `./hyperion.config.json`)
	- `--gui` for gui
	- `--json` for network connection (`--host=<ip> --port=<port>`)
	- `--help` to see all options
11. Play some audio
12. Levels should be drawn to gui, also sent to hyperion if json enabled
13. Exit by closing the GUI or Ctrl+c

### Installation and running on OSMC (RPi 2)

1. Enable audio so we can use alsa and loopback: Add `dtparam=audio=on` to `/boot/config.txt`.
  - Why? https://discourse.osmc.tv/t/alsa-doesnt-work-after-last-update/10600
2. Install Gstreamer 1.0, alsa, PyGI and pip: `sudo apt-get install libgstreamer1.0-0 gir1.2-gstreamer-1.0 gir1.2-glib-2.0 gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-good gstreamer1.0-tools gstreamer1.0-alsa alsa-base alsa-utils python-gi python-pip`
3. Install git (`sudo apt-get install git`) and clone this repo (`git clone https://github.com/RanzQ/hyperion-audio-effects.git`), or just download as zip and extract
4. Install python dependencies `cd hyperion-audio-effects/ && sudo pip install -r requirements.txt`
5. Put `options snd-aloop index=-2` in end of `/etc/modprobe.d/alsa-base.conf` (the file doesn't exist, just create it) to prevent loopback device for getting first card index
6. Enable loopback device `sudo modprobe snd-aloop` (and type line `snd-aloop` to /etc/modules to make it permanent)
7. Included are 2 different asound configuration files: `asound.conf.loopback` and `asound.conf.mic`. Choose `asound.conf.mic`, if you have a microphone attached to your Raspberry pi through e.g. an external USB sound card. The sound levels recorded by the microphone will be used to create the effects. If you do not have a microphone, use `asound.conf.loopback` to utilize the loopback device.
8. Rename the chosen asound configuration file to  `.asoundrc` and copy it to your home folder (backup old if exists) and change the soundcard index if needed (`"hw:<card>,<device>"`, check `aplay -l`) *
9. Reboot
10. Now you must choose how to play some music. Kodi/OSMC doesn't support the loopback setup and Spotify can't be installed (maybe possible soon, check [spotifyd](https://github.com/Spotifyd/spotifyd)), so I went with mpd and mpc `sudo apt-get install mpd mpc`.
  - To get audio working with `mpd`, I needed to copy the alsa config to be global `sudo cp .asoundrc /etc/asound.conf`
  - After adding some music to `/var/lib/mpd/music` run `mpc ls | mpc add` to add all files to playlist, then `mpc play` (check `mpc help` for all commands).
  - You can select between HDMI and Headphone jack with `amixer cset numid=3 2` (HDMI) / `amixer cset numid=3 1` (Headphone)
  - I didn't find a way to adjust the audio level that the effects receives, I've done that using Spotify
11. Finally you can try the audio-effects :)
  - `cd hyperion-audio-effects/`
  - `python main.py --effect vumeter`
  - The heavier effect works with setting `"band-width-exp": 4-5` but uses quite a lot of CPU. `python main.py --effect color_spectrum`
  - You can also modify `config.json` and just run `python main.py`
  - Exit by typing `x` and enter

### Effects development
1. Copy one of the script & config pairs in `effects/` (e.g. `myeffect.py` and `myeffect.json`) and then it can be passed as `--effect=myeffect` (json values can be read from `hyperion.args` like in normal hyperion effects)
2. Adjust gstreamer parameters
   - See `spectrum_dump.py` for explanation of parameters for GstSpectrumDump
   - Using `vumeter` and `bands` you can adjust the type of received magnitudes (`self.magnitudes`)
      * With `vumeter=True` you get 4 magnitudes which correspond to peaks and decays for the L/R channels
      * With `vumeter=False` you get spectrum magnitudes for the amount of `bands` (defaults to 128)
3. Update the leds by modifying the bytearray `self.ledsData` according to values in `self.magnitudes` (I've done it in method `update_leds()`)

### Effect: VU Meter
- Volume bars for left and right of your hyperion setup, or by setting indices manually
- Min and max volume and colors can be adjusted from config

### Effect: Color spectrum
- Leds strip is divided into octaves 1-8
- Low frequencies start from red, ending in pink at high frequencies
- Adjust your sound volume if the leds are too dim or bright (no volume normalization yet)
- Config has a field `band-width-exp`, if you have performance issues, try with higher values (it sets FFT bin size to 2^x Hz, e.g. 2^3 = 8 Hz, affects on bass accuracy)
- Set `mirror` to false if you want to use whole strip instead of splitting and mirroring
- TODO: Adjustable colors
- New config parameter `matrix`
  - Modified version for matrix setups, need to use protobuf connection instead of json
  - Disable black border detection in hyperion config for this to work properly

\* Check this if you have pulseaudio: [#4](https://github.com/RanzQ/hyperion-audio-effects/issues/4#issuecomment-67764593)

\** Windows instructions were removed since performance was poor due to the fact that Gstreamer is meant for Linux


### Webserver
`webserver.py` contains a simple HTTP interface to control the effects of hyperion-audio-effects as well as the effects that are available with hyperion. It also allows to shutdown the Raspberry Pi.

###### Installation
1. Execute `./webserver.py` or `python webserver.py` as normal user and check, if the script is working. 
2. If you would like to start the webserver everytime the Raspberry Pi boots, follow the instructions given in `webserver.service`

