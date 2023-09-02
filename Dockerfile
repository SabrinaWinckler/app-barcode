# Definir uma imagem base do Ubuntu que possui o OpenJDK 8
FROM ubuntu:20.04

# Definir variável de ambiente para evitar interação durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instalar as dependências necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    openjdk-8-jdk \
    unzip \
    curl \
    git \
    autoconf

# Fazer o download e instalar o Android SDK
RUN curl -o sdk-tools.zip https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip
RUN unzip sdk-tools.zip -d /opt/android-sdk
RUN rm sdk-tools.zip

# Configurar variáveis de ambiente
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="${PATH}:${ANDROID_HOME}/tools/bin:${ANDROID_HOME}/platform-tools"

# Atualizar o SDK do Android e aceitar as licenças automaticamente
RUN yes | $ANDROID_HOME/tools/bin/sdkmanager --licenses


# Instalar as dependências de compilação necessárias
RUN apt-get update && apt-get install -y autoconf automake libtool libffi-dev libssl-dev


# Instalar o pacote zip
RUN apt-get update && apt-get install -y zip

RUN apt-get update && apt-get install -y libsdl2-mixer-dev libsdl2-ttf-dev sqlite3 libsqlite3-dev



# Copiar o código-fonte do aplicativo para o contêiner
COPY . /app-barcode
WORKDIR /app-barcode

# Instalar as dependências do projeto (se estiverem listadas em requirements.txt)
RUN pip3 install -r requirements.txt

# Instalar o Python e outras dependências
RUN pip3 install Kivy
RUN pip3 install Cython
# Instalar o Python e outras dependências
RUN pip3 install --upgrade python-for-android

# Atualizar o buildozer e instalar a plataforma Android
RUN pip3 install --upgrade buildozer

# RUN yes | buildozer android clean
# Executar o buildozer android update
# RUN yes | buildozer android update

# Compilar o APK com o buildozer (você pode escolher debug ou release)
# RUN buildozer android debug

# Para executar o aplicativo no emulador ou dispositivo Android, use:
# RUN buildozer android deploy run

# Para limpar a construção do APK, use:
# RUN buildozer android clean

# Se você quiser executar comandos interativamente dentro do contêiner
# para depurar ou testar, você pode executar o seguinte:
# CMD ["/bin/bash"]
