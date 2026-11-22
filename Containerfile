FROM alpine 

RUN apk add --no-cache fish python3 vim
RUN /usr/bin/fish -c "set -U fish_greeting"

WORKDIR /root/cyberwarn

COPY __init__.py .
COPY packages.txt .
COPY data data/
COPY cyberwarn cyberwarn/
COPY tests tests/
RUN find . -iname "__pycache__" -exec rm -rf {} +

RUN python3 -m venv venv && ./venv/bin/pip install -r packages.txt
RUN echo "source /root/cyberwarn/venv/bin/activate.fish" > /root/.config/fish/config.fish
CMD ["fish"]
