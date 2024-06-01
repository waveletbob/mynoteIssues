FROM alphine:latest
RUN apk update && apk add --no-cache ubuntu-minimal && rm -rf /var/cache/apk/*
CMD ["/bin/sh"]