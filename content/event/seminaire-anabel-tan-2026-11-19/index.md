---
generated_by: scripts/import_seminars.py
title: "Séminaire — Anabel Tan"
event: "Colloques et séminaires"
summary: "TransformerRIM: A Multi-Resolution, Data-Driven Transformer Framework for Radio Interferometric Imaging with Uncertainty Quantification"
abstract: >-
  Radio interferometric imaging reconstructs sky brightness distributions from sparse Fourier measurements, forming a highly ill-posed inverse problem that is increasingly challenged by the scale and resolution demands of next-generation telescopes, such as the Square Kilometre Array (SKA). Classical approaches, including CLEAN and its variants, often struggle with extended emission and face significant challenges in scaling to high-throughput, high-dynamic-range observations. We propose a multi-resolution, data-driven transformer framework for radio interferometric imaging that integrates learnt image priors with physics-based measurement constraints. The reconstruction update is modelled using a Swin Transformer architecture, enabling long-range spatial modelling and multi-scale feature representation. To support end-to-end optimisation, we develop a custom CUDA-based differentiable measurement operator that efficiently implements forward and adjoint mappings between sky brightness and irregularly sampled visibilities, with each mapping computed in milliseconds, enabling scalable training and inference. Building on this foundation, we develop a coarse-to-fine multi-resolution reconstruction strategy that progressively refines image estimates across image scales, improving stability and computational efficiency in large-scale problems. In addition, we incorporate a diffusion-based generative component to model reconstruction uncertainty. The proposed framework provides a scalable and flexible approach to data-driven interferometric imaging, designed to address the computational and statistical challenges of next-generation radio astronomy pipelines.
presenter: "Anabel Tan"
presenter_institution: "UdeM"
date: "2026-11-19T13:30:00-05:00"
date_end: "2026-11-19T14:30:00-05:00"
all_day: false
location: "A-2553, Campus MIL de l'Université de Montréal"
authors: []
draft: false
profile: false
share: false
featured: false
---

## Titre

TransformerRIM: A Multi-Resolution, Data-Driven Transformer Framework for Radio Interferometric Imaging with Uncertainty Quantification

## Résumé

Radio interferometric imaging reconstructs sky brightness distributions from sparse Fourier measurements, forming a highly ill-posed inverse problem that is increasingly challenged by the scale and resolution demands of next-generation telescopes, such as the Square Kilometre Array (SKA). Classical approaches, including CLEAN and its variants, often struggle with extended emission and face significant challenges in scaling to high-throughput, high-dynamic-range observations. We propose a multi-resolution, data-driven transformer framework for radio interferometric imaging that integrates learnt image priors with physics-based measurement constraints. The reconstruction update is modelled using a Swin Transformer architecture, enabling long-range spatial modelling and multi-scale feature representation. To support end-to-end optimisation, we develop a custom CUDA-based differentiable measurement operator that efficiently implements forward and adjoint mappings between sky brightness and irregularly sampled visibilities, with each mapping computed in milliseconds, enabling scalable training and inference. Building on this foundation, we develop a coarse-to-fine multi-resolution reconstruction strategy that progressively refines image estimates across image scales, improving stability and computational efficiency in large-scale problems. In addition, we incorporate a diffusion-based generative component to model reconstruction uncertainty. The proposed framework provides a scalable and flexible approach to data-driven interferometric imaging, designed to address the computational and statistical challenges of next-generation radio astronomy pipelines.
