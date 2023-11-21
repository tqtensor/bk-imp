#import "@preview/polylux:0.3.1": *
#import themes.university: *

#set page(paper: "presentation-16-9")
#set text(font: "Times New Roman")
#set text(size: 25pt)

#show: university-theme.with(
  short-author: "Thai. T. Q.",
  short-title: "Bahnaric Phoneme Segmentation",
)

#title-slide(
  authors: ("Tang Quoc Thai"),
  title: "Project I: Bahnaric Phoneme Segmentation",
  subtitle: "Supervised by Assoc. Prof. Quan Thanh Tho",
  date: "21-Nov-2023",
  institution-name: "Ho Chi Minh University of Technology",
  logo: image("hcmut_official_logo.png", width: 30mm)
)

#slide(title: [Motivation])[
  #align(horizon + left)[
    === Objective:
    Empower Bahnaric language speakers, fostering communication within their ethnic community and with other ethnic groups.

    === Significance of Phoneme Segmentation:
    - Create a precise phoneme-level mapping for the Bahnaric language.
    - Enable the development of advanced Text-to-Speech (TTS) and Automatic Speech Recognition (ASR) models.

    === Overall Goal:
    Contribute to the empowerment and connectivity of Bahnaric ethnic communities through targeted advancements in speech processing.
  ]
]

#slide(title: [Bahnaric Phoneme])[
  #side-by-side(gutter: 3mm, columns: (1fr, 2fr))[
    #align(horizon + left)[
      - The phoneme sample consists of single words, and each word is pronounced by a native speaker.
      - The beginning and ending time of each phoneme marked by the 'ov' and 'op' label respectively.
    ]
  ][
    #image("phoneme_example.png")
  ]
]

#slide(title: [Feature Engineering])[
  The following features are extracted from the audio clips:
    #align(horizon + left)[
      #text(size: 15pt)[
        - *MFCC* (Mel Frequency Cepstral Coefficients): These are coefficients that collectively make up an MFC. They are derived from a type of cepstral representation of the audio clip (a nonlinear "spectrum-of-a-spectrum").
        - *Zero Crossings*: This is the rate at which the signal changes from positive to negative or back.
        - *Mel Spectrogram*: A Mel Spectrogram is a spectrogram where the frequencies are converted to the Mel scale.
        - *Harmonics*: These are integer multiples of the base frequency in a sound. They contribute to the perceived timbre of a sound.
        - *Spectral Centroids*: It indicates where the "center of mass" of the spectrum is located. It is used in digital signal processing to identify the brightness of a sound.
        - *Chromagram*: A chromagram is a graphical representation of the chroma of a signal. In music, the chroma of a note is its position within the octave of the twelve-note chromatic scale.
        - *Tempo BPM* (Beats Per Minute): This is a measure of tempo in music, indicating the number of beats occurring in one minute.
        - *Spectral Bandwidth*: This is the difference between the highest and lowest frequencies in a continuous band of frequencies. It can be used to identify the smoothness of a sound.
    ]
  ]
]

#slide(title: [Feature Engineering])[
  #side-by-side(gutter: 3mm, columns: (2fr, 1fr))[
    #align(horizon + left)[
      - The phoneme sample consists of single words, and each word is pronounced by a native speaker.
      - The procedure of feature extraction is as follows:
    #text(size: 15pt)[
      ```python
      for audio_clip in audio_clips:
        audio_clip_features = []
        for frame in audio_clip:
            frame_features = []
            for feature in acoustic_features:
                for window_length in range(85, 126, 10):
                    windowed_audio = get_window(frame, window_length)
                    mean_value = calculate_mean(window, feature)
                    frame_features.append("feature_name_window_length", mean_value)
            audio_clip_features.append("audio_clip_name": frame_features)
      ```
      ]
    ]
  ][
    #image("features.png")
  ]
]

#slide(title: [Labels])[
  #align(horizon + left)[
    - The 'ov' and 'op' labels are extracted from the TextGrid files.
    - The information obtained reveals the timestamps of these markers in milliseconds. Consequently, it is necessary to convert these timestamps into frame indices, with each frame corresponding to a 5ms interval.
    - *A strong assumption* has been made: the neighboring frames of the 'ov' and 'op' labels are also labeled as 'ov' and 'op' respectively.
  ]
]

#slide(title: [Training])[
  #side-by-side(gutter: 3mm, columns: (1fr, 1fr))[
    #align(horizon + left)[
      - Each frame is treated as a data point, and the label is either 0 or 1.
      - The extended labels are the the neighboring frames of the 'ov' or 'op' labels.
      - LGBMClassifier is used to train two separate models for the 'ov' and 'op' labels.
    ]
  ][
    #image("training.png")
  ]
]

#matrix-slide[
  left
][
  middle
][
  right
]

#matrix-slide(columns: 1)[
  top
][
  bottom
]

#matrix-slide(columns: (1fr, 2fr, 1fr), ..(lorem(8),) * 9)

#focus-slide(background-img: image("background.svg"))[
  #set align(horizon + center)
  = *Thank You*
]
