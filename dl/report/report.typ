#import "template.typ": *
#let title = "Assignment: Training HiFi-GAN on Bahnaric Language"
#let author = "Tang Quoc Thai"
#let course_id = "CO5255"
#let instructor = "Le Thanh Sach"
#let semester = "Spring 2023"
#set enum(numbering: "a)")
#set heading(numbering: "1.1)")
#set par(justify: true)
#set text(lang:"en", hyphenate:true)
#show: assignment_class.with(title, author, course_id, instructor, semester)

*Source code*: https://github.com/tqtensor/hifi-gan

= Project Description

In this deep learning course project, the focus will be on enhancing the quality of generated voice for the Bahnaric language using advanced techniques in the field of deep learning. The Bahnaric language is an ethnic language with limited available resources, particularly in the domain of voice synthesis. While collecting speech data for the Bahnaric language is part of a larger project, this course project specifically aims to improve the voice generation quality for this underrepresented language.

== Motivation

Voice synthesis, a crucial component of human-computer interaction, has witnessed significant advancements thanks to deep learning. However, most of the existing high-quality voice generation models, such as vocoders, are primarily trained on widely spoken languages like English and Chinese. For lesser-known languages like Bahnaric, the absence of specialized models results in voice synthesis that lacks authenticity, fluency, and naturalness. The motivation behind this project is to address this gap and pioneer the development of a vocoder that is pre-trained on Bahnaric speech data, thus significantly enhancing the quality and accuracy of voice generation for this ethnic language.

== Understanding Vocoder

A vocoder, short for voice encoder, is a deep learning model used for voice synthesis and manipulation. It takes an input speech signal and separates it into different components like the pitch, spectral envelope, and modulation, allowing for the manipulation and generation of artificial voices. Vocoder models have been highly successful in generating realistic human-like speech and have found applications in various fields, including entertainment, assistive technology, and communication.

== Advantages of Pretraining with Ethnic Language

Pretraining a vocoder with an ethnic language like Bahnaric offers several advantages that can lead to significant breakthroughs:

- Cultural and Linguistic Nuances: Ethnic languages often have unique phonetic and linguistic characteristics that are not present in widely spoken languages. By pretraining a vocoder on Bahnaric data, the model can capture these specific nuances, resulting in more accurate and authentic voice generation.

- Improved Fluency and Naturalness: Training a vocoder on Bahnaric speech data will help it learn the subtle variations, intonations, and cadences that are specific to the language. This will lead to generated voices that sound more natural and fluent, closely resembling the way native speakers of Bahnaric speak.

- Reduced Data Scarcity: Ethnic languages typically have limited available data, making it challenging to train high-quality models from scratch. By leveraging pretrained models on more widely available data, the project can alleviate the data scarcity issue and still achieve impressive results.

- Pioneering Research: Developing a vocoder pretrained on an ethnic language like Bahnaric is a novel and pioneering endeavor. This research can contribute to the broader field of voice synthesis and inspire further work on enhancing voice generation for other underrepresented languages.

= Background Theory

#figure(
  image("hifigan_model.jpg", width: 80%),
  caption: [Model Architecture of HiFi-GAN],
)

== Generator

The generator in the HiFi-GAN architecture is a convolutional neural network (CNN) responsible for transforming mel-spectrograms into raw waveform audio signals. It follows a fully convolutional design and employs transposed convolutions to upsample the input mel-spectrogram until its temporal resolution matches that of raw waveforms.

== Discriminators

In the context of the HiFi-GAN paper, the discriminators are designed to address the challenges of modeling realistic speech audio, particularly focusing on long-term dependencies and diverse periodic patterns present in speech signals. The paper introduces two types of discriminators: the Multi-Period Discriminator (MPD) and the Multi-Scale Discriminator (MSD).

=== Multi-Period Discriminator (MPD)

The MPD is designed to identify the diverse periodic patterns present in speech audio. Speech signals consist of sinusoidal signals with various periods, and these underlying periodic patterns need to be accurately identified for high-quality voice synthesis. The MPD consists of several sub-discriminators, each responsible for handling a specific portion of periodic signals in the input audio. This approach allows the MPD to effectively capture and analyze different periodic components within the audio signal.

=== Multi-Scale Discriminator (MSD)

The MSD is employed to capture consecutive patterns and long-term dependencies within the audio data. The idea behind the MSD is to evaluate audio samples at different levels of granularity. This is achieved by consecutively processing the audio samples with multiple scales, enabling the discriminator to analyze the audio signal at varying resolutions. The MSD technique is inspired by the multi-scale discriminator introduced in the MelGAN paper (Kumar et al., 2019).

= Dataset

#figure(
  image("bahnaric_dataset.jpeg", width: 100%),
  caption: [Dataset for Bahnaric Language],
)

Our dataset for improving Bahnaric language voice generation was meticulously crafted. We downloaded Bahnaric news videos from VTV5 and extracted the audio. Using power analysis, we split the audio into 15-second clips containing human speech, filtering out non-speech parts. This resulted in a substantial dataset of 316 hours of diverse Bahnaric speech. This dataset forms the foundation for training our voice enhancement model, ensuring authenticity and linguistic richness for improved voice generation.

= Modification of HiFi-GAN

The forked repository for this project can be located at https://github.com/tqtensor/hifi-gan. In this repository, the code for preparing the Baharic dataset has been added. Modifications have also been made to the training code to enable the model's training on the Bahnaric dataset. The training process utilizes two GPUs and reaches the similar loss as compared with the original model, concluding after 1,000,000 iterations.

```python
import glob
from collections import defaultdict

if __name__ == "__main__":
    # Collect all the original videos
    file_paths = sorted(glob.glob("BahnaricSpeech/wavs/*.wav"))
    original_videos = defaultdict(list)
    for file_path in file_paths:
        video_id = file_path[:-8]
        original_videos[video_id].append(file_path)

    # Use the original videos to split the data into train, val
    train_videos = list(original_videos.keys())[: int(len(original_videos) * 0.95)]
    val_videos = list(original_videos.keys() - set(train_videos))

    train_audios = sum([original_videos[video_id] for video_id in train_videos], [])
    val_audios = sum([original_videos[video_id] for video_id in val_videos], [])

    # Save the split into a file
    with open("BahnaricSpeech/training.txt", "w") as f:
        f.write("\n".join(train_audios))
    with open("BahnaricSpeech/validation.txt", "w") as f:
        f.write("\n".join(val_audios))
```

= Validation Loss
== Original HiFi-GAN
#figure(
  image("validation_loss_original.png", width: 80%),
  caption: [Validation Loss of Original HiFi-GAN],
)

== Bahnaric HiFi-GAN
#figure(
  image("validation_loss_bahnaric.png", width: 80%),
  caption: [Validation Loss of Bahnaric HiFi-GAN],
)

= References

Kong, J., Kim, J. and Bae, J. (2020) HiFi-Gan: Generative adversarial networks for efficient and high fidelity speech synthesis, arXiv.org. Available at: https://arxiv.org/abs/2010.05646.

Kumar, K. et al. (2019) Melgan: Generative adversarial networks for conditional waveform synthesis, arXiv.org. Available at: https://arxiv.org/abs/1910.06711.
