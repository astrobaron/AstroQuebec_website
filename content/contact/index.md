---
title: Nous joindre
date: 2022-10-24

type: landing

sections:
  - block: contact
    content:
      title: Nous joindre
      text: |-
        Pour joindre AstroQuébec, proposer une collaboration, annoncer une activité ou contacter une personne ressource, écrivez-nous en indiquant brièvement votre affiliation et l’objet de votre message.
      email: contact@example.org
      phone: ''
      address:
        street: ''
        city: Quebec
        region: QC
        postcode: ''
        country: Canada
        country_code: CA
      coordinates:
        latitude: '46.8139'
        longitude: '-71.2080'
      directions: Rencontres sur rendez-vous.
      office_hours:
        - 'Sur rendez-vous'
      appointment_url: ''
      #contact_links:
      #  - icon: comments
      #    icon_pack: fas
      #    name: Discuss on Forum
      #    link: 'https://discourse.gohugo.io'
    
      # Automatically link email and phone or display as text?
      autolink: true
    
      # Email form provider
      form:
        provider: netlify
        formspree:
          id:
        netlify:
          # Enable CAPTCHA challenge to reduce spam?
          captcha: false
    design:
      columns: '1'

  - block: markdown
    content:
      title:
      subtitle: ''
      text:
    design:
      columns: '1'
      background:
        image: 
          filename: astroquebec-research.png
          filters:
            brightness: 1
          parallax: false
          position: center
          size: cover
          text_color_light: true
      spacing:
        padding: ['20px', '0', '20px', '0']
      css_class: fullscreen
---
