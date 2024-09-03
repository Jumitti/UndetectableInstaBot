# UndetectableInstaBot

## Overview

**UndetectableInstaBot** is an Instagram bot designed to seamlessly like and comment on posts by mimicking human interaction. Inspired by a bug in Beeper that flagged it as an Instagram bot, I discovered that most Instagram bot programs are quickly detected and blocked. Thus, I decided to develop a different approach: a bot that's "undetectable because it behaves like a human clicking."

## Description

UndetectableInstaBot identifies areas for likes and comments using image recognition technology. Once these areas are detected, it automatically performs likes and comments on Instagram posts. The goal is to create a bot that closely mimics human behavior, reducing the chances of detection by Instagram's security measures.

## Installation
**Requirement: Python 3.10 and above**

**On WINDOWS:**
1. Clone the repository (or download and extract [HERE](https://github.com/Jumitti/UndetectableInstaBot/archive/refs/heads/master.zip)):
    ```bash
    git clone https://github.com/Jumitti/UndetectableInstaBot.git
    ```
2. Double-clic on ``install.bat`` and wait installation of requirements. That all 😎
3. For future uses, you can just run ``run.bat``

**On MAC and LINUX (not tested)
1. Clone the repository (or download and extract [HERE](https://github.com/Jumitti/UndetectableInstaBot/archive/refs/heads/master.zip)):
    ```bash
    git clone https://github.com/Jumitti/UndetectableInstaBot.git
    ```
2. Go to the root of the folder and open your terminal. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Always with the terminal. Run the bot:
    - Run `pithon run.py` (Note: Not yet tested on these platforms)

[HERE](https://youtu.be/2SWTaooFhFg) Tutorial video (coming soon)

## Usage

UndetectableInstaBot features a graphical user interface (GUI) with the following functionalities:

- **Threshold Settings**: Adjust the recognition thresholds for likes and comments (1 = disabled).
- **Comment Lists**: Load custom comment lists from `.txt` files in the `comment_list` folder.
- **Randomization**: Enable randomization of comments and selection of 1 to 3 emojis when emojis are configured.
- **Debug Mode**: Save screenshots and analyze recognition zones for likes and comments.
- **Dark Mode Detection**: Automatically detects if the Instagram page is in dark mode.
- **Control Buttons**:
  - **Start**: Initiates the bot and configures it to detect like and comment areas.
  - **Pause**: Pauses the bot without resetting the current state.
  - **Stop**: Stops the bot and resets its configurations.

### Limitations

One known limitation is that UndetectableInstaBot takes control of the mouse, preventing you from using the PC simultaneously. This is a trade-off for avoiding detection as a bot.

## Upcoming Features

- Improved performance and accuracy
- Hashtag search functionality
- Automatic follow feature

## Contributors

- **[Julien Minniti](https://github.com/Jumitti)** - Sole contributor

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

> **Disclaimer**<a name="disclaimer" />: Please note that this is a research project. I am by no means responsible for any usage of this tool. Use it on your behalf. I'm also not responsible if your accounts get banned due to the extensive use of this tool.