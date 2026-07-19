---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        AstroQuébec
      image:
        filename: main_image.jpg
        credit: "Crédit photo : AstroQuébec"
      text: |
        <br>
        
        Le Centre de recherche en astrophysique du Québec (AstroQuébec) est un regroupement interdisciplinaire dont la mission est de Comprendre l’Univers, soit son origine, son évolution, sa structure, ses constituants, et notre place en son sein. 

  - block: collection
    content:
      title: Nouvelles
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
      title: Notre mission
      subtitle: ''
      text: |
        La mission d’AstroQuébec est de soutenir une recherche scientifique de pointe en astronomie et en astrophysique, de former la prochaine génération de spécialistes et de faire rayonner l’astronomie québécoise sur la scène nationale et internationale.

        Le centre met en commun l’expertise en observations, instrumentation, modélisation et analyse de données afin de mieux comprendre les planètes, les étoiles, les galaxies et l’évolution de l’Univers.
    design:
      columns: '1'

  - block: markdown
    id: activites
    content:
      title: Activités
      subtitle: ''
      text: |
        Les membres d’AstroQuébec organisent et participent à des séminaires, colloques, écoles d’été, ateliers de formation, activités publiques et rencontres scientifiques. Ces activités favorisent la collaboration, la diffusion des résultats et le partage des outils de recherche.
    design:
      columns: '1'

  - block: markdown
    id: presentation
    content:
      title: Présentation
      subtitle: ''
      text: |
        AstroQuébec regroupe des chercheuses, chercheurs, étudiantes, étudiants et partenaires qui travaillent sur les grandes questions de l’astrophysique moderne. Ses projets couvrent les exoplanètes, la formation stellaire, les galaxies, les trous noirs, l’Univers lointain et les instruments qui rendent ces découvertes possibles.
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
        {{% cta cta_link="./people/" cta_text="Consulter le répertoire" %}}
    design:
      columns: '1'
---
