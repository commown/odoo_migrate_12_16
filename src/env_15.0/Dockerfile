# <OOW> : Copy of https://github.com/odoo/odoo/blob/15.0/setup/package.dfsrc
FROM debian:bullseye
MAINTAINER Odoo S.A. <info@odoo.com>

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/*

# Reconfigure locales such that postgresql uses UTF-8 encoding
RUN dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install \
        dh-python \
        packaging-dev \
        postgresql \
        postgresql-client \
        adduser \
        python3-pip \
        build-essential \
        python3-babel \
        python3-dateutil \
        python3-decorator \
        python3-docutils \
        python3-gevent \
        python3-pil \
        python3-jinja2 \
        python3-libsass \
        python3-lxml \
        python3-ofxparse \
        python3-passlib \
        python3-polib \
        python3-psutil \
        python3-psycopg2 \
        python3-pydot \
        python3-openssl \
        python3-pypdf2 \
        python3-qrcode \
        python3-renderpm \
        python3-reportlab \
        python3-requests \
        python3-serial \
        python3-setuptools \
        python3-stdnum \
        python3-tz \
        python3-usb \
        python3-vobject \
        python3-werkzeug \
        python3-xlsxwriter \
        python3-xlrd \
        python3-zeep \
        rsync \
        python3 -y && \
    rm -rf /var/lib/apt/lists/*

# <OOW> Install Debian packages
 COPY extra_debian_requirements.txt /extra_debian_requirements.txt
 RUN apt-get update -qq \
    && apt-get install -y git \
    && xargs apt-get install -y --no-install-recommends <extra_debian_requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# <OOW> Install Python librairies
COPY extra_python_requirements.txt /extra_python_requirements.txt
RUN apt clean
RUN pip3 install --upgrade pip \
    && python3 -m pip install --no-cache-dir setuptools-scm \
    && python3 -m pip install --no-cache-dir -r /extra_python_requirements.txt

RUN pip3 install --upgrade pyopenssl \
    && pip3 install cryptography==38

# <OOW> Get local user id and set it to the odoo user
ARG LOCAL_USER_ID

RUN useradd --uid $LOCAL_USER_ID --non-unique odoo

USER odoo
