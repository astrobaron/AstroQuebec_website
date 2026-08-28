---
title:
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        AstroQuébec
      image:
        filename: 2024_rencontre_annuelle.jpeg
        credit: "Image credit: AstroQuébec"
      text: |
        <br>

        The Center for Research in Astrophysics of Quebec (AstroQuébec) is an interdisciplinary organisation whose mission is to understand the Universe – its origin, evolution, structure, constituents, and our place within it.

  - block: collection
    content:
      title: News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '2'

  - block: markdown
    id: mission
    content:
      title: Our Mission
      subtitle: ''
      text: |
        AstroQuébec supports leading research in astronomy and astrophysics, trains the next generation of specialists, and helps Quebec astronomy shine nationally and internationally.

        The centre brings together expertise in observations, instrumentation, modeling, and data analysis to better understand planets, stars, galaxies, and the evolution of the Universe.
    design:
      columns: '1'

  - block: markdown
    id: activites
    content:
      title: Activities
      subtitle: ''
      text: |
        AstroQuébec members organize and participate in seminars, colloquia, summer schools, training workshops, public activities, and scientific meetings. These activities support collaboration, research communication, and the sharing of research tools.
    design:
      columns: '1'

  - block: markdown
    id: presentation
    content:
      title: Overview
      subtitle: ''
      text: |
        AstroQuébec brings together researchers, students, and partners working on major questions in modern astrophysics. Its projects span exoplanets, star formation, galaxies, black holes, the distant Universe, and the instruments that make these discoveries possible.
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
            brightness: 0.75
          parallax: false
          position: center
          size: cover
          text_color_light: true
      spacing:
        padding: ['20px', '0', '20px', '0']
      css_class: fullscreen

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Browse the directory" %}}
    design:
      columns: '1'
---
