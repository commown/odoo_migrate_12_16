# <OOW> : Copy of https://github.com/odoo/odoo/blob/13.0/setup/package.dfsrc
FROM debian:buster

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/*

# Reconfigure locales such that postgresql uses UTF-8 encoding
RUN dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update -qq &&  \
    apt-get upgrade -qq -y && \
    apt-get install \
        postgresql \
        postgresql-server-dev-all \
        postgresql-client \
        adduser \
        libsass1 \
        libxml2-dev \
        libxslt1-dev \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        python3-dev \
        python3-pip \
        python3-wheel \
        build-essential \
        python3 -y && \
    rm -rf /var/lib/apt/lists/*

# <OOW> Install Debian packages
COPY extra_debian_requirements.txt /extra_debian_requirements.txt
RUN apt-get update -qq \
    && apt-get install -y git \
    && xargs apt-get install -y --no-install-recommends <extra_debian_requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# <OOW> Install Python librairies
COPY ./src/odoo/requirements.txt /odoo_python_requirements.txt
COPY extra_python_requirements.txt /extra_python_requirements.txt
RUN pip3 install --upgrade pip \
    && python3 -m pip install --no-cache-dir setuptools-scm \
    && python3 -m pip install --no-cache-dir -r /odoo_python_requirements.txt \
    && python3 -m pip install --no-cache-dir -r /extra_python_requirements.txt

# <OOW> Get local user id and set it to the odoo user
ARG LOCAL_USER_ID

RUN useradd --uid $LOCAL_USER_ID --non-unique odoo

USER odoo
