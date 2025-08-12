# bangla-plagiarism-check
A Bangla plagiarism detection tool that analyzes text for similarities using advanced natural language processing, helping identify copied or paraphrased content in Bengali language with high accuracy.

#python3.10
##switch to python 3.10


<pre> ```bash

# Update & install prerequisites
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl llvm libncursesw5-dev \
xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Install pyenv
curl https://pyenv.run | bash

# Setup environment (bash)
echo -e '\n# pyenv config' >> ~/.bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.10
pyenv install 3.10.13
pyenv global 3.10.13

# Verify
python --version

``` </pre>


# use Python 3.10 in your project directory only

<pre> ```bash
cd /path/to/your/project
pyenv local 3.10.13
python --version 

``` </pre>


# Create env

<pre> ```bash
python -m venv venv
source venv/bin/activate

``` </pre>
