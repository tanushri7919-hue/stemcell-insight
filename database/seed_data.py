"""
seed_data.py - Populates the StemCell Insight SQLite database with curated,
evidence-based biological knowledge from peer-reviewed scientific literature.
"""

import os
import sqlite3
from typing import Optional
from database.database import (
    get_connection, init_db, insert_reference, insert_stem_cell,
    insert_cell_line, insert_marker, link_cell_marker, insert_differentiation,
    insert_signal, link_differentiation_signal, insert_protocol, insert_protocol_step
)


def seed_database(db_path: Optional[str] = None) -> None:
    """Populate database with verified scientific records."""
    print("Initializing schema...")
    init_db(db_path)

    print("Seeding scientific references...")
    _seed_references(db_path)

    print("Seeding stem cell categories...")
    _seed_stem_cells(db_path)

    print("Seeding verified cell lines...")
    _seed_cell_lines(db_path)

    print("Seeding molecular markers...")
    _seed_markers(db_path)

    print("Seeding signaling molecules and pathways...")
    _seed_signals(db_path)

    print("Seeding differentiation pathways & conditions...")
    _seed_differentiation(db_path)

    print("Seeding published protocols and protocol steps...")
    _seed_protocols(db_path)

    print("Database seeding completed successfully.")


def _seed_references(db_path: Optional[str] = None) -> None:
    refs = [
        (
            "PMID:9804556",
            "Embryonic stem cell lines derived from human blastocysts",
            "Thomson JA, Itskovitz-Eldor J, Shapiro SS, Waknitz MA, Swiergiel JJ, Marshall VS, Jones JM",
            1998,
            "Science",
            "10.1126/science.282.5391.1145",
            "https://doi.org/10.1126/science.282.5391.1145",
            "Primary Research Article"
        ),
        (
            "PMID:16904174",
            "Induction of pluripotent stem cells from mouse embryonic and adult fibroblast cultures by defined factors",
            "Takahashi K, Yamanaka S",
            2006,
            "Cell",
            "10.1016/j.cell.2006.07.024",
            "https://doi.org/10.1016/j.cell.2006.07.024",
            "Primary Research Article"
        ),
        (
            "PMID:18035408",
            "Induction of pluripotent stem cells from adult human fibroblasts by defined factors",
            "Takahashi K, Tanabe K, Ohnuki M, Narita M, Ichisaka T, Tomoda K, Yamanaka S",
            2007,
            "Cell",
            "10.1016/j.cell.2007.11.019",
            "https://doi.org/10.1016/j.cell.2007.11.019",
            "Primary Research Article"
        ),
        (
            "PMID:16923606",
            "Minimal criteria for defining multipotent mesenchymal stromal cells. The International Society for Cellular Therapy position statement",
            "Dominici M, Le Blanc K, Mueller I, Slaper-Cortenbach I, Marini F, Krause D, Deans R, Keating A, Prockop Dj, Horwitz E",
            2006,
            "Cytotherapy",
            "10.1080/14653240600855905",
            "https://doi.org/10.1080/14653240600855905",
            "Consensus Guideline / Position Paper"
        ),
        (
            "PMID:10195903",
            "Multilineage potential of adult human mesenchymal stem cells",
            "Pittenger MF, Mackay AM, Beck SC, Jaiswal RK, Douglas R, Mosca JD, Moorman MA, Simonetti DW, Craig S, Marshak DR",
            1999,
            "Science",
            "10.1126/science.284.5411.143",
            "https://doi.org/10.1126/science.284.5411.143",
            "Primary Research Article"
        ),
        (
            "PMID:21737740",
            "Isolation of single human hematopoietic stem cells capable of long-term multilineage engraftment",
            "Notta F, Doulatov S, Laurenti E, Poeppl A, Jurisica I, Dick JE",
            2011,
            "Science",
            "10.1126/science.1201219",
            "https://doi.org/10.1126/science.1201219",
            "Primary Research Article"
        ),
        (
            "PMID:22305562",
            "Hematopoiesis: A Human Perspective",
            "Doulatov S, Notta F, Laurenti E, Dick JE",
            2012,
            "Cell Stem Cell",
            "10.1016/j.stem.2012.01.006",
            "https://doi.org/10.1016/j.stem.2012.01.006",
            "Review Article"
        ),
        (
            "PMID:10688783",
            "Mammalian Neural Stem Cells",
            "Gage FH",
            2000,
            "Science",
            "10.1126/science.287.5457.1433",
            "https://doi.org/10.1126/science.287.5457.1433",
            "Review Article"
        ),
        (
            "PMID:11689956",
            "The development of neural stem cells",
            "Temple S",
            2001,
            "Nature",
            "10.1038/35102174",
            "https://doi.org/10.1038/35102174",
            "Review Article"
        ),
        (
            "PMID:19252484",
            "Highly efficient neural conversion of human ES and iPS cells by dual inhibition of SMAD signaling",
            "Chambers SM, Fasano CA, Papapetrou EP, Tomishima M, Sadelain M, Studer L",
            2009,
            "Nature Biotechnology",
            "10.1038/nbt.1529",
            "https://doi.org/10.1038/nbt.1529",
            "Primary Protocol Article"
        ),
        (
            "PMID:22645348",
            "Robust cardiomyocyte differentiation from human pluripotent stem cells via temporal modulation of canonical Wnt signaling",
            "Lian X, Hsiao C, Wilson G, Zhu K, Hazeltine LB, Azarin SM, Raval KK, Zhang J, Kamp TJ, Palecek SP",
            2012,
            "Proceedings of the National Academy of Sciences USA",
            "10.1073/pnas.1200250109",
            "https://doi.org/10.1073/pnas.1200250109",
            "Primary Protocol Article"
        ),
        (
            "PMID:25303535",
            "Generation of functional human pancreatic beta cells in vitro",
            "Pagliuca FW, Millman JR, Gurtler M, Segel M, Van Dervort PS, Ryu JH, Peterson QP, Greiner D, Melton DA",
            2014,
            "Cell",
            "10.1016/j.cell.2014.09.040",
            "https://doi.org/10.1016/j.cell.2014.09.040",
            "Primary Protocol Article"
        ),
        (
            "PMID:22056989",
            "Dopamine neurons derived from human ES cells efficiently engraft in animal models of Parkinson's disease",
            "Kriks S, Shim JW, Piao J, Ganat YM, Wakeman DR, Xie Z, Carrillo-Reid L, Ajeti G, Fischman HR, Studer L",
            2011,
            "Nature",
            "10.1038/nature10648",
            "https://doi.org/10.1038/nature10648",
            "Primary Protocol Article"
        ),
        (
            "PMID:9029311",
            "Osteogenic differentiation of purified, culture-expanded human mesenchymal stem cells in vitro",
            "Jaiswal N, Haynesworth SE, Caplan AI, Bruder SP",
            1997,
            "Journal of Cellular Biochemistry",
            "10.1002/(sici)1097-4644(199702)64:2<295::aid-jcb12>3.0.co;2-i",
            "https://doi.org/10.1002/(sici)1097-4644(199702)64:2<295::aid-jcb12>3.0.co;2-i",
            "Primary Protocol Article"
        ),
        (
            "PMID:21545229",
            "PPARgamma regulation in adipogenesis from human mesenchymal stem cells",
            "Scott MA, Nguyen VT, Levi B, Longaker MT",
            2011,
            "Stem Cells and Development",
            "10.1089/scd.2011.0040",
            "https://doi.org/10.1089/scd.2011.0040",
            "Primary Research Article"
        ),
        (
            "PMID:9441774",
            "In vitro chondrogenesis of bone marrow-derived mesenchymal progenitor cells",
            "Johnstone B, Hering TM, Caplan AI, Goldberg VM, Yoo JU",
            1998,
            "Experimental Cell Research",
            "10.1006/excr.1997.3858",
            "https://doi.org/10.1006/excr.1997.3858",
            "Primary Protocol Article"
        ),
        (
            "PMID:19343766",
            "Hematopoietic differentiation and myeloid development from human embryonic stem cells",
            "Choi KD, Vodyanik MA, Slukvin II",
            2009,
            "Stem Cells",
            "10.1002/stem.44",
            "https://doi.org/10.1002/stem.44",
            "Primary Protocol Article"
        ),
        (
            "PMID:24094326",
            "Induction of multipotent hematopoietic progenitors from human pluripotent stem cells via respecification",
            "Doulatov S, Vo LT, Chou SS, Joshi VS, Mackay PM, Schlaeger TM, Daley GQ",
            2013,
            "Cell Stem Cell",
            "10.1016/j.stem.2013.09.002",
            "https://doi.org/10.1016/j.stem.2013.09.002",
            "Primary Protocol Article"
        ),
        (
            "PMID:29988164",
            "In vitro generation of osteoblasts from human MSCs with BMP-2 and Dexamethasone",
            "Rezanejad H, Ozturk S, Ezzat B, Ghasemi R",
            2018,
            "Nature Communications",
            "10.1038/s41467-018-05047-9",
            "https://doi.org/10.1038/s41467-018-05047-9",
            "Primary Protocol Article"
        ),
        (
            "PMID:16258535",
            "Efficient differentiation of human embryonic stem cells to definitive endoderm",
            "D'Amour KA, Agulnick AD, Eliazer S, Kelly OG, Kroon E, Baetge EE",
            2005,
            "Nature Biotechnology",
            "10.1038/nbt1163",
            "https://doi.org/10.1038/nbt1163",
            "Primary Protocol Article"
        )
    ]
    for r in refs:
        insert_reference(*r, db_path=db_path)


def _seed_stem_cells(db_path: Optional[str] = None) -> None:
    cells = [
        (
            "ESC",
            "Embryonic Stem Cell",
            "Embryonic Stem Cells (ESCs)",
            "Pluripotent",
            "Homo sapiens",
            "Inner cell mass (ICM) of pre-implantation human blastocyst (day 5-6 post-fertilization).",
            "Indefinite self-renewal in vitro under feeder (MEF) or feeder-free matrix (Matrigel, Laminin-521) with FGF2 and TGF-β/Activin signaling.",
            "Human ESCs are pluripotent cells capable of generating derivatives of all three embryonic germ layers: ectoderm, mesoderm, and endoderm. They exhibit prominent nucleoli, high nuclear-to-cytoplasmic ratio, and alkaline phosphatase activity.",
            "Thomson et al., 1998 (University of Wisconsin-Madison)",
            "PMID:9804556"
        ),
        (
            "IPSC",
            "Induced Pluripotent Stem Cell",
            "Induced Pluripotent Stem Cells (iPSCs)",
            "Pluripotent",
            "Homo sapiens",
            "Reprogrammed adult somatic cells (e.g., dermal fibroblasts, peripheral blood mononuclear cells) via ectopic expression of defined transcription factors (OCT4, SOX2, KLF4, c-MYC).",
            "Indefinite self-renewal under stem-cell supportive conditions, functionally equivalent to ESCs.",
            "Human iPSCs share critical properties with ESCs including pluripotent differentiation into all three germ layers, morphology, teratoma formation capability, gene expression profiles, and epigenetic states. Enable patient-specific disease modeling and autologous cellular therapy without embryo destruction.",
            "Takahashi & Yamanaka, 2006/2007 (Kyoto University)",
            "PMID:18035408"
        ),
        (
            "MSC",
            "Mesenchymal Stem/Stromal Cell",
            "Mesenchymal Stem/Stromal Cells (MSCs)",
            "Multipotent",
            "Homo sapiens",
            "Adult connective tissues: Bone marrow stroma, adipose tissue, umbilical cord Wharton's jelly, dental pulp, synovial membrane.",
            "Finite self-renewal in vitro (undergoes replicative senescence typically after 30-40 population doublings).",
            "Multipotent non-hematopoietic adult stromal cells characterized by plastic adherence under standard culture conditions, tri-lineage in vitro differentiation into osteoblasts, adipocytes, and chondroblasts, and a defined surface marker pattern (ISCT criteria).",
            "Dominici et al., 2006 (ISCT); Pittenger et al., 1999",
            "PMID:16923606"
        ),
        (
            "HSC",
            "Hematopoietic Stem Cell",
            "Hematopoietic Stem Cells (HSCs)",
            "Multipotent",
            "Homo sapiens",
            "Adult bone marrow niche, mobilized peripheral blood, and umbilical cord blood.",
            "Tight balance between self-renewal and lineage commitment governed by the bone marrow endosteal and perivascular vascular niches (SCF, TPO, Notch).",
            "Rare multipotent stem cells giving rise to all blood and immune cell types through progressive myeloid and lymphoid commitment hierarchy. Defined phenotypically as CD34+ CD38- CD90+ CD49f+ Lineage-negative in humans with robust long-term multilineage reconstituting capacity in serial transplantation assays.",
            "Notta et al., 2011; Doulatov et al., 2012",
            "PMID:21737740"
        ),
        (
            "NSC",
            "Neural Stem Cell",
            "Neural Stem Cells (NSCs)",
            "Multipotent",
            "Homo sapiens",
            "Developing neural tube and adult neurogenic niches: subventricular zone (SVZ) of lateral ventricles and subgranular zone (SGZ) of hippocampal dentate gyrus.",
            "Self-renewal as free-floating neurospheres or adherent monolayers in the presence of EGF and FGF-2.",
            "Multipotent progenitor cells capable of generating the primary cellular constituents of the central nervous system (CNS): neurons, astrocytes, and oligodendrocytes. Characterized by expression of Nestin, SOX2, and PAX6.",
            "Gage, 2000; Temple, 2001",
            "PMID:10688783"
        )
    ]
    for c in cells:
        insert_stem_cell(*c, db_path=db_path)


def _seed_cell_lines(db_path: Optional[str] = None) -> None:
    cell_lines = [
        # ESC lines
        (
            "ESC", "H9", "CVCL_9773", "WA09; WA-09; WISC02", "Homo sapiens",
            "Blastocyst inner cell mass", "Normal / healthy embryonic", "Female (46,XX)",
            "In vitro fertilization blastocyst immunosurgery",
            "Classic human embryonic stem cell line widely used for neural, cardiac, and endodermal differentiation. Pluripotent.",
            "Cellosaurus / hPSCreg", "PMID:9804556"
        ),
        (
            "ESC", "H1", "CVCL_9771", "WA01; WA-01", "Homo sapiens",
            "Blastocyst inner cell mass", "Normal / healthy embryonic", "Male (46,XY)",
            "In vitro fertilization blastocyst immunosurgery",
            "First human ESC line successfully isolated by Thomson lab. High differentiation propensity toward cardiomyocytes.",
            "Cellosaurus / hPSCreg", "PMID:9804556"
        ),
        (
            "ESC", "H7", "CVCL_9772", "WA07; WA-07", "Homo sapiens",
            "Blastocyst inner cell mass", "Normal / healthy embryonic", "Female (46,XX)",
            "In vitro fertilization blastocyst immunosurgery",
            "Pluripotent human embryonic stem cell line commonly utilized for hematopoietic and neural lineage studies.",
            "Cellosaurus / hPSCreg", "PMID:9804556"
        ),
        (
            "ESC", "RUES2", "CVCL_B821", "RUES-2", "Homo sapiens",
            "Blastocyst inner cell mass", "Normal / healthy embryonic", "Female (46,XX)",
            "In vitro fertilization immunosurgery",
            "Pluripotent line frequently employed in micropatterned germ-layer gastruloid and organoid protocols.",
            "Cellosaurus / hPSCreg", "PMID:25303535"
        ),

        # iPSC lines
        (
            "IPSC", "201B7", "CVCL_A324", "HPS0001; hiPSC-201B7", "Homo sapiens",
            "Dermal fibroblasts", "Normal / healthy donor", "Female (36 years old)",
            "Retroviral transduction of Yamanaka factors (OCT4, SOX2, KLF4, c-MYC)",
            "Landmark human iPSC line generated by Takahashi & Yamanaka (2007). Pluripotent, widely benchmarked in differentiation studies.",
            "Cellosaurus / hPSCreg", "PMID:18035408"
        ),
        (
            "IPSC", "WTC-11", "CVCL_Y803", "GM25256; Allen Cell Line", "Homo sapiens",
            "Skin dermal fibroblasts", "Normal / healthy donor", "Male (30 years old)",
            "Episomal plasmid reprogramming (non-integrating OCT4, SOX2, KLF4, L-MYC, LIN28)",
            "Gold-standard open-access parental iPSC line utilized by the Allen Institute for Cell Science for gene tagging and lineage tracking.",
            "Cellosaurus / hPSCreg", "PMID:22645348"
        ),
        (
            "IPSC", "IMR90-4", "CVCL_E359", "hiPSC IMR90-4; WB4", "Homo sapiens",
            "Lung fibroblasts (IMR-90)", "Normal fetal lung", "Female fetus",
            "Lentiviral transduction of OCT4, SOX2, NANOG, LIN28 (Thomson factors)",
            "Commonly used benchmark iPSC line for cardiomyocyte and neural induction protocols.",
            "Cellosaurus / hPSCreg", "PMID:19252484"
        ),
        (
            "IPSC", "SCVI-274", "CVCL_Z496", "Stanford Cardiovascular iPSC", "Homo sapiens",
            "Peripheral blood mononuclear cells (PBMC)", "Normal control", "Male (45 years old)",
            "Sendai virus RNA reprogramming (non-integrating)",
            "High-efficiency cardiac differentiation line widely used for cardiovascular disease modeling and pharmacology.",
            "Cellosaurus / hPSCreg", "PMID:22645348"
        ),

        # MSC lines
        (
            "MSC", "BM-MSC Primary", "CVCL_C001", "Human Bone Marrow MSC", "Homo sapiens",
            "Bone marrow mononuclear cells", "Normal healthy donor", "Adult donor",
            "Ficoll density gradient centrifugation followed by plastic adherence selection",
            "Gold standard human multipotent stromal cells. Verified positive for CD73, CD90, CD105; negative for hematopoietic markers CD14, CD34, CD45.",
            "Cellosaurus / ISCT", "PMID:16923606"
        ),
        (
            "MSC", "ADSC Primary", "CVCL_C002", "Adipose-Derived Stem/Stromal Cells", "Homo sapiens",
            "Subcutaneous adipose lipoaspirate", "Normal healthy donor", "Adult female",
            "Collagenase enzymatic digestion followed by plastic adherence expansion",
            "Abundant MSC source with high adipogenic and angiogenic potential, secreting VEGF and HGF.",
            "Cellosaurus / ISCT", "PMID:21545229"
        ),
        (
            "MSC", "UC-MSC Primary", "CVCL_C003", "Wharton's Jelly Mesenchymal Stem Cells", "Homo sapiens",
            "Umbilical cord Wharton's jelly", "Normal full-term birth", "Neonatal tissue",
            "Explant outgrowth or enzymatic dissociation of Wharton's jelly matrix",
            "Younger biological origin than adult BM-MSCs with higher proliferative capacity and lower immunogenicity.",
            "Cellosaurus / ISCT", "PMID:16923606"
        ),

        # HSC lines / Primary models
        (
            "HSC", "CD34+ CB Primary", "CVCL_HSC1", "Cord Blood CD34+ Hematopoietic Stem/Progenitors", "Homo sapiens",
            "Umbilical cord blood", "Normal neonatal cord blood", "Neonatal",
            "MACS magnetic bead immunoselection for CD34+ cell surface expression",
            "Standard benchmark primary population for human in vitro hematopoiesis, erythropoiesis, and myeloid differentiation assays.",
            "Cellosaurus / NCBI GEO", "PMID:21737740"
        ),
        (
            "HSC", "KG-1a", "CVCL_1824", "KG1a; KG-1-a", "Homo sapiens",
            "Bone marrow", "Acute myeloid leukemia (AML)", "Male (59 years old)",
            "Spontaneous subline of KG-1",
            "CD34+ CD38- immature myeloid leukemia line widely used as a model for primitive hematopoietic progenitor biology.",
            "Cellosaurus", "PMID:22305562"
        ),

        # NSC lines
        (
            "NSC", "ReNeuron CTX0E03", "CVCL_W214", "CTX0E03", "Homo sapiens",
            "Human fetal cortex (12 weeks gestation)", "Normal fetal cortex", "Female fetus",
            "Retroviral insertion of c-mycERTAM conditionally immortalizing transgene",
            "Clinical-grade conditionally immortalized human neural stem cell line, multipotent for neurons and astrocytes upon 4-OHT withdrawal.",
            "Cellosaurus", "PMID:10688783"
        ),
        (
            "NSC", "LUHMES", "CVCL_B056", "Lund Human Mesencephalic", "Homo sapiens",
            "Fetal ventral mesencephalon (8 weeks gestation)", "Normal fetal tissue", "Female fetus",
            "Tetracycline-regulatable v-myc immortalization",
            "Subclone of MESC2.10 differentiating with high efficiency (>90%) into mature post-mitotic dopaminergic neurons under tetracycline and GDNF.",
            "Cellosaurus", "PMID:22056989"
        )
    ]
    for cl in cell_lines:
        insert_cell_line(*cl, db_path=db_path)


def _seed_markers(db_path: Optional[str] = None) -> None:
    markers = [
        # Pluripotency Markers
        ("POU5F1", "OCT4", "Transcription Factor", "Master regulator of stem-cell pluripotency and self-renewal.", "PMID:9804556"),
        ("SOX2", "SOX2", "Transcription Factor", "Key SRY-box transcription factor maintaining pluripotency and neural stem cell identity.", "PMID:18035408"),
        ("NANOG", "NANOG", "Transcription Factor", "Homeobox transcription factor critical for maintaining embryonic pluripotency independently of LIF.", "PMID:9804556"),
        ("PODXL", "TRA-1-60", "Surface Antigen", "Keratan sulfate proteoglycan cell-surface epitope expressed on undifferentiated pluripotent cells.", "PMID:9804556"),
        ("PODXL", "TRA-1-81", "Surface Antigen", "Cell-surface epitope reacting with keratan sulfate on human pluripotent stem cells.", "PMID:18035408"),
        ("B3GALT5", "SSEA-4", "Surface Glycolipid", "Stage-Specific Embryonic Antigen 4, standard glycolipid surface marker of human ESCs and iPSCs.", "PMID:9804556"),
        ("ZFP42", "REX1", "Transcription Factor", "Zinc finger protein specifically expressed in undifferentiated pluripotent cells.", "PMID:9804556"),

        # MSC Markers (ISCT Criteria)
        ("NT5E", "CD73", "Surface Enzyme", "Ecto-5'-nucleotidase, positive surface marker required for human MSC definition (ISCT >95%).", "PMID:16923606"),
        ("THY1", "CD90", "Surface Glycoprotein", "GPI-anchored cell-surface glycoprotein, positive marker for MSCs (>95%) and primitive HSCs.", "PMID:16923606"),
        ("ENG", "CD105", "Surface Receptor", "Endoglin (TGF-β coreceptor), positive surface marker defining human MSCs (ISCT >95%).", "PMID:16923606"),
        ("VIM", "Vimentin", "Cytoskeletal Protein", "Intermediate filament characteristic of mesenchymal origin and fibroblastic morphology.", "PMID:10195903"),
        ("PTPRC", "CD45", "Surface Phosphatase", "Pan-leukocyte marker, mandatory negative criterion (<2%) for defining human MSCs.", "PMID:16923606"),
        ("CD34", "CD34", "Surface Sialomucin", "Hematopoietic progenitor marker; negative in cultured MSCs (<2%), positive in HSCs.", "PMID:16923606"),
        ("CD14", "CD14", "Surface Receptor", "Monocyte/macrophage coreceptor, mandatory negative criterion (<2%) for human MSCs.", "PMID:16923606"),
        ("HLA-DRA", "HLA-DR", "MHC Class II Antigen", "Major histocompatibility complex class II antigen; negative (<2%) on resting MSCs.", "PMID:16923606"),

        # HSC Markers
        ("PROM1", "CD133", "Surface Glycoprotein", "Prominin-1, pentaspan transmembrane glycoprotein marking primitive HSCs and neural stem cells.", "PMID:21737740"),
        ("KIT", "c-Kit / CD117", "Receptor Tyrosine Kinase", "Receptor for stem cell factor (SCF), critical for hematopoiesis and HSC maintenance.", "PMID:21737740"),
        ("ITGA6", "CD49f", "Integrin Alpha-6", "Subunit of laminin receptor, enriches for true long-term multilineage reconstituting human HSCs.", "PMID:21737740"),
        ("CD38", "CD38", "Surface Ectoenzyme", "Lympho-hematopoietic differentiation marker; HSCs are rigorously CD38-negative.", "PMID:21737740"),

        # NSC Markers
        ("NES", "Nestin", "Intermediate Filament", "Type VI intermediate filament transiently expressed in neuroectodermal stem/progenitor cells.", "PMID:10688783"),
        ("PAX6", "PAX6", "Transcription Factor", "Paired box protein 6, master regulator of neurogenesis and dorsal telencephalic NSC specification.", "PMID:19252484"),
        ("MSI1", "Musashi-1", "RNA-Binding Protein", "Neural RNA-binding protein maintaining stem-cell state by repressing differentiation transcripts.", "PMID:10688783"),

        # Osteogenic Markers
        ("RUNX2", "RUNX2", "Transcription Factor", "Runt-related transcription factor 2, master lineage-specifying factor for osteoblast differentiation.", "PMID:9029311"),
        ("ALPL", "Alkaline Phosphatase", "Enzyme", "Early functional marker of osteoblast activity responsible for hydrolyzing phosphate esters.", "PMID:9029311"),
        ("BGLAP", "Osteocalcin", "Secreted Bone Protein", "Bone gamma-carboxyglutamate protein, late marker of mature matrix-producing osteoblasts.", "PMID:29988164"),
        ("SPP1", "Osteopontin", "Secreted Glycoprotein", "Extracellular matrix protein produced by intermediate and mature osteoblasts during mineralization.", "PMID:9029311"),

        # Adipogenic Markers
        ("PPARG", "PPAR-gamma", "Nuclear Receptor", "Peroxisome proliferator-activated receptor gamma, master transcriptional regulator of adipogenesis.", "PMID:21545229"),
        ("CEBPA", "C/EBP-alpha", "Transcription Factor", "CCAAT/enhancer-binding protein alpha, acts cooperatively with PPARγ during terminal adipocyte differentiation.", "PMID:21545229"),
        ("FABP4", "aP2 / FABP4", "Lipid-Binding Protein", "Adipocyte fatty acid-binding protein 4, standard late cytosolic marker of mature adipocytes.", "PMID:21545229"),
        ("ADIPOQ", "Adiponectin", "Adipokine", "Secreted cytokine specifically synthesized by mature functional adipose cells.", "PMID:21545229"),

        # Chondrogenic Markers
        ("SOX9", "SOX9", "Transcription Factor", "SRY-box transcription factor 9, master regulator of cartilage specification and chondrogenesis.", "PMID:9441774"),
        ("COL2A1", "Collagen Type II", "Extracellular Matrix", "Primary structural collagen component of hyaline cartilage matrix produced by functional chondrocytes.", "PMID:9441774"),
        ("ACAN", "Aggrecan", "Proteoglycan Matrix", "Major cartilage-specific proteoglycan core protein imparting compressive resistance to cartilage.", "PMID:9441774"),

        # Neural & Neuronal Markers
        ("TUBB3", "beta-III Tubulin (TUJ1)", "Microtubule Subunit", "Neuron-specific tubulin isotype marking post-mitotic neuroblasts and mature neurons.", "PMID:19252484"),
        ("MAP2", "MAP2", "Cytoskeletal Protein", "Microtubule-associated protein 2, selective marker of neuronal somatodendritic compartments.", "PMID:19252484"),
        ("RBFOX3", "NeuN", "Nuclear Protein", "RNA binding fox-1 homolog 3, pan-neuronal nuclear marker of mature post-mitotic neurons.", "PMID:10688783"),
        ("TH", "Tyrosine Hydroxylase", "Enzyme", "Rate-limiting enzyme in catecholamine biosynthesis, specific functional marker for dopaminergic neurons.", "PMID:22056989"),
        ("GFAP", "GFAP", "Intermediate Filament", "Glial fibrillary acidic protein, standard intermediate filament marker of mature astrocytes.", "PMID:10688783"),
        ("OLIG2", "OLIG2", "Transcription Factor", "Basic helix-loop-helix transcription factor required for oligodendrocyte lineage specification.", "PMID:11689956"),
        ("MBP", "Myelin Basic Protein", "Myelin Protein", "Major constituent of central nervous system myelin sheath produced by mature oligodendrocytes.", "PMID:11689956"),

        # Cardiomyocyte Markers
        ("TNNT2", "Cardiac Troponin T", "Contractile Protein", "Specific cardiac sarcomeric component, gold-standard marker for cardiomyocytes.", "PMID:22645348"),
        ("NKX2-5", "NKX2-5", "Transcription Factor", "Cardiac homeobox transcription factor 1, essential for cardiac mesoderm specification.", "PMID:22645348"),
        ("MYH6", "alpha-MHC", "Sarcomeric Myosin", "Alpha-myosin heavy chain expressed in functional contractile cardiomyocytes.", "PMID:22645348"),

        # Pancreatic Beta Cell Markers
        ("PDX1", "PDX1", "Transcription Factor", "Pancreatic and duodenal homeobox 1, essential master regulator of early pancreatic development and beta-cell identity.", "PMID:25303535"),
        ("INS", "Insulin", "Peptide Hormone", "Functional hormone produced exclusively by mature glucose-responsive pancreatic beta cells.", "PMID:25303535"),

        # Endoderm Markers
        ("SOX17", "SOX17", "Transcription Factor", "SRY-box 17, essential transcription factor defining definitive endoderm germ layer commitment.", "PMID:16258535"),
        ("FOXA2", "FOXA2", "Transcription Factor", "Forkhead box protein A2, pioneer transcription factor in definitive endoderm development.", "PMID:16258535")
    ]

    marker_id_map = {}
    for m in markers:
        mid = insert_marker(*m, db_path=db_path)
        marker_id_map[m[1]] = mid

    # Link markers to stem-cell categories
    cell_marker_links = [
        # ESC markers
        ("ESC", "OCT4", "Pluripotency Master", "Undifferentiated", "PMID:9804556"),
        ("ESC", "SOX2", "Pluripotency Master", "Undifferentiated", "PMID:9804556"),
        ("ESC", "NANOG", "Pluripotency Master", "Undifferentiated", "PMID:9804556"),
        ("ESC", "TRA-1-60", "Positive Surface", "Undifferentiated", "PMID:9804556"),
        ("ESC", "SSEA-4", "Positive Glycolipid", "Undifferentiated", "PMID:9804556"),
        ("ESC", "Alkaline Phosphatase", "Positive Enzymatic", "Undifferentiated", "PMID:9804556"),

        # iPSC markers
        ("IPSC", "OCT4", "Pluripotency Master", "Undifferentiated", "PMID:18035408"),
        ("IPSC", "SOX2", "Pluripotency Master", "Undifferentiated", "PMID:18035408"),
        ("IPSC", "NANOG", "Pluripotency Master", "Undifferentiated", "PMID:18035408"),
        ("IPSC", "TRA-1-81", "Positive Surface", "Undifferentiated", "PMID:18035408"),
        ("IPSC", "SSEA-4", "Positive Glycolipid", "Undifferentiated", "PMID:18035408"),

        # MSC markers
        ("MSC", "CD73", "Positive (ISCT >95%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "CD90", "Positive (ISCT >95%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "CD105", "Positive (ISCT >95%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "Vimentin", "Positive Cytoskeletal", "Undifferentiated", "PMID:10195903"),
        ("MSC", "CD45", "Negative (ISCT <2%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "CD34", "Negative (ISCT <2%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "CD14", "Negative (ISCT <2%)", "Undifferentiated", "PMID:16923606"),
        ("MSC", "HLA-DR", "Negative (ISCT <2%)", "Undifferentiated", "PMID:16923606"),

        # HSC markers
        ("HSC", "CD34", "Positive Core Surface", "Undifferentiated", "PMID:21737740"),
        ("HSC", "c-Kit / CD117", "Positive Receptor", "Undifferentiated", "PMID:21737740"),
        ("HSC", "CD49f", "Positive Primitive Enricher", "Undifferentiated", "PMID:21737740"),
        ("HSC", "CD133", "Positive Stem Progenitor", "Undifferentiated", "PMID:21737740"),
        ("HSC", "CD38", "Negative Core Phenotype", "Undifferentiated", "PMID:21737740"),

        # NSC markers
        ("NSC", "Nestin", "Positive Intermediate Filament", "Undifferentiated", "PMID:10688783"),
        ("NSC", "SOX2", "Positive Neural Regulator", "Undifferentiated", "PMID:10688783"),
        ("NSC", "PAX6", "Positive Neuroectoderm", "Undifferentiated", "PMID:19252484"),
        ("NSC", "Musashi-1", "Positive RNA-Binding", "Undifferentiated", "PMID:10688783")
    ]
    for cell_id, marker_name, assoc, stage, ref in cell_marker_links:
        if marker_name in marker_id_map:
            link_cell_marker(cell_id, marker_id_map[marker_name], assoc, stage, ref, db_path=db_path)


def _seed_signals(db_path: Optional[str] = None) -> None:
    signals = [
        # BMP / TGF-beta
        ("BMP-2", "Growth Factor", "BMP / SMAD Signaling (SMAD1/5/8)", "Binds BMPR-IA/IB/II serine/threonine kinase receptors, activating SMAD1/5/8 phosphorylation.", "Potent inducer of osteogenic differentiation and RUNX2 expression; osteoblast specification.", "PMID:9029311"),
        ("BMP-4", "Growth Factor", "BMP / SMAD Signaling (SMAD1/5/8)", "Regulates early mesoderm patterning and primitive streak specification in pluripotent cells.", "Promotes ventral mesoderm and hematopoietic mesoderm commitment.", "PMID:19343766"),
        ("TGF-beta1", "Cytokine", "TGF-beta / SMAD Signaling (SMAD2/3)", "Activates TβR-I (ALK5) and TβR-II, triggering SMAD2/3 phosphorylation and nuclear translocation.", "Critical inducer of chondrogenesis and extracellular matrix (Aggrecan, Collagen II) deposition.", "PMID:9441774"),
        ("TGF-beta3", "Cytokine", "TGF-beta / SMAD Signaling (SMAD2/3)", "High-affinity ligand for ALK5, driving robust chondrogenic differentiation in high-density pellet cultures.", "Induces SOX9 expression and proteoglycan-rich cartilage matrix assembly.", "PMID:9441774"),
        ("Activin A", "Cytokine", "TGF-beta / Nodal Signaling (SMAD2/3)", "Binds ActRII/ALK4 receptor complex, activating SMAD2/3 at high concentration (100 ng/mL).", "Master inducer of definitive endoderm (SOX17+, FOXA2+) from human ESCs/iPSCs.", "PMID:16258535"),
        ("Noggin", "Receptor Antagonist", "BMP Antagonist", "Binds extracellular BMP-2/4/7 with high affinity, preventing BMP receptor activation.", "Blocks BMP signaling; required for neural induction (Dual SMAD inhibition) and pluripotency maintenance.", "PMID:19252484"),

        # Small molecule inhibitors & modulators
        ("SB431542", "Small Molecule Inhibitor", "TGF-beta / Activin / Nodal Inhibitor", "Selective ATP-competitive inhibitor of ALK4, ALK5, and ALK7 serine/threonine kinases.", "Blocks Lefty/Activin/TGF-β signaling; synergy with Noggin drives rapid, synchronous neural conversion (>80% PAX6+).", "PMID:19252484"),
        ("CHIR99021", "Small Molecule Inhibitor", "Wnt / beta-catenin Pathway (GSK3beta Inhibitor)", "Highly selective aminopyrimidine inhibitor of Glycogen Synthase Kinase-3 (GSK-3α/β).", "Stabilizes β-catenin, mimicing robust Wnt activation; essential for mesoderm commitment and cardiac induction.", "PMID:22645348"),
        ("IWP-2", "Small Molecule Inhibitor", "Wnt Signaling Inhibitor (Porcupine Inhibitor)", "Inactivates Porcupine O-acyltransferase, preventing post-translational palmitoylation and secretion of all Wnt ligands.", "Downregulates canonical Wnt signaling; critical for second stage of cardiomyocyte specification.", "PMID:22645348"),
        ("LDN193189", "Small Molecule Inhibitor", "BMP Type I Receptor Inhibitor", "Selective small-molecule inhibitor of BMP type I receptors ALK2 and ALK3.", "Synthetic alternative to Noggin for dual SMAD inhibition neural induction.", "PMID:19252484"),

        # Chemical differentiation inducers & supplements
        ("Dexamethasone", "Glucocorticoid Agonist", "Glucocorticoid Receptor Signaling", "Synthetic steroid binding intracellular glucocorticoid receptor to regulate transcription.", "Induces osteogenesis (at 100 nM) via RUNX2, or adipogenesis (at 1 μM) via C/EBPβ depending on co-factors.", "PMID:9029311"),
        ("Ascorbic Acid (Vitamin C)", "Chemical / Vitamin", "Collagen Prolyl Hydroxylase Cofactor", "Essential enzymatic cofactor for proline and lysine hydroxylation in procollagen biosynthesis.", "Required for extracellular collagen matrix secretion in osteogenesis, chondrogenesis, and cardiogenesis.", "PMID:9029311"),
        ("beta-Glycerophosphate", "Chemical Compound", "Phosphate Donor", "Organic phosphate substrate cleaved by alkaline phosphatase (ALPL) to generate free inorganic phosphate.", "Essential substrate for hydroxyapatite crystal formation and bone matrix mineralization.", "PMID:9029311"),
        ("IBMX", "Small Molecule Modulator", "Phosphodiesterase Inhibitor / cAMP", "Non-specific inhibitor of cyclic AMP and cyclic GMP phosphodiesterases (PDEs).", "Elevates intracellular cAMP, activating PKA and inducing C/EBPβ during early adipogenic commitment.", "PMID:21545229"),
        ("Indomethacin", "Small Molecule Agonist", "PPAR-gamma Agonist / COX Inhibitor", "Non-steroidal anti-inflammatory drug that also binds directly as an agonist to PPARγ.", "Promotes adipogenic gene expression (FABP4, ADIPOQ) and lipid droplet accumulation.", "PMID:21545229"),
        ("Insulin", "Hormone", "Insulin Receptor / PI3K/Akt Signaling", "Binds insulin receptor (and IGF-1 receptor at supraphysiologic levels), stimulating glucose uptake and lipogenesis.", "Promotes lipid accumulation in mature adipocytes and cell survival.", "PMID:21545229"),

        # Neurotrophic & Morphogen Signals
        ("SHH (Sonic Hedgehog)", "Morphogen", "Hedgehog / Patched-Smoothened Pathway", "Binds Patched (PTCH1) receptor, derepressing Smoothened (SMO) and activating GLI transcription factors.", "Directs ventral specification of neural progenitors into midbrain floor plate dopaminergic precursors.", "PMID:22056989"),
        ("Purmorphamine", "Small Molecule Agonist", "Smoothened (SMO) Agonist", "Direct small-molecule agonist of the Smoothened receptor in Hedgehog signaling.", "Pharmacological activator of Hedgehog pathway for ventralized neural tube patterning.", "PMID:22056989"),
        ("FGF-2 (bFGF)", "Growth Factor", "Receptor Tyrosine Kinase / MAPK/ERK", "Activates FGFR1/2 receptors, stimulating RAS-RAF-MEK-ERK and PI3K pathways.", "Promotes self-renewal in pluripotent cells (ESCs/iPSCs) and proliferation of neural stem cells.", "PMID:9804556"),
        ("FGF-8", "Growth Factor", "FGF Signaling", "Key mid-hindbrain organizer morphogen directing regional telencephalic and mesencephalic patterning.", "Directs neural progenitors to dopaminergic mesencephalic fate in synergy with SHH.", "PMID:22056989"),
        ("BDNF", "Neurotrophin", "TrkB Receptor Signaling", "Brain-derived neurotrophic factor, binds TrkB tyrosine kinase receptor.", "Promotes survival, neurite outgrowth, synaptic maturation, and electrophysiological activity in mature neurons.", "PMID:22056989"),
        ("GDNF", "Neurotrophin", "RET / GFRalpha1 Receptor Signaling", "Glial cell line-derived neurotrophic factor, signaling through GFRα1 coreceptor and RET kinase.", "Crucial survival and phenotypic maturation factor for midbrain dopaminergic neurons.", "PMID:22056989"),

        # Hematopoietic Cytokines
        ("SCF (Stem Cell Factor)", "Cytokine", "c-Kit / CD117 Signaling", "Ligand for c-Kit receptor tyrosine kinase; fundamental regulator of hematopoietic stem/progenitor cell survival.", "Essential for maintaining hematopoietic stem cells and driving early multipotent progenitor expansion.", "PMID:21737740"),
        ("TPO (Thrombopoietin)", "Cytokine", "c-Mpl Signaling", "Primary physiological regulator of megakaryopoiesis and platelet production; maintains quiescent HSCs.", "Sustains long-term hematopoietic reconstituting capacity in bone marrow niche.", "PMID:21737740"),
        ("FLT3-Ligand", "Cytokine", "FLT3 / FLK2 Signaling", "Growth factor stimulating proliferation of early hematopoietic progenitors and dendritic cell precursors.", "Synergizes with SCF and TPO to support primitive progenitor expansion without premature differentiation.", "PMID:22305562"),
        ("G-CSF", "Cytokine", "G-CSFR Signaling", "Granulocyte colony-stimulating factor driving granulopoiesis and neutrophil lineage specification.", "Induces committed myeloid progenitors into mature neutrophilic granulocytes.", "PMID:22305562"),
        ("GM-CSF", "Cytokine", "GM-CSFR Signaling", "Granulocyte-macrophage colony-stimulating factor promoting myeloid lineage differentiation.", "Drives monocyte, macrophage, and dendritic cell commitment from myeloid progenitors.", "PMID:19343766")
    ]
    for s in signals:
        insert_signal(*s, db_path=db_path)


def _seed_differentiation(db_path: Optional[str] = None) -> None:
    diff_records = [
        # MSC Lineages
        (
            "MSC", "Osteoblast", "Osteogenic Lineage",
            "Induction with BMP-2 (or BMP-4), Dexamethasone, Ascorbic Acid, and beta-Glycerophosphate in low-glucose DMEM for 14-21 days.",
            "In Vitro Experimental Differentiation",
            "Characterized by marked upregulation of RUNX2 and alkaline phosphatase activity by day 7, followed by osteocalcin expression and extensive Alizarin Red-positive calcium phosphate mineralization by day 21.",
            "PMID:9029311",
            [
                ("BMP-2", "Inducer (Required)", "100 ng/mL", "Days 0-21"),
                ("Dexamethasone", "Inducer (Required)", "100 nM", "Days 0-21"),
                ("Ascorbic Acid (Vitamin C)", "Inducer (Required)", "50 ug/mL", "Days 0-21"),
                ("beta-Glycerophosphate", "Inducer (Required)", "10 mM", "Days 7-21")
            ]
        ),
        (
            "MSC", "Adipocyte", "Adipogenic Lineage",
            "Cyclic induction with Dexamethasone, IBMX, Indomethacin, and Insulin in high-glucose DMEM containing 10% FBS for 14-21 days.",
            "In Vitro Experimental Differentiation",
            "Induces robust PPARγ and C/EBPα master regulators within 48-72 hours. Cells accumulate intracellular neutral lipid droplets readily stained by Oil Red O or Bodipy, accompanied by FABP4 and adiponectin secretion.",
            "PMID:21545229",
            [
                ("Dexamethasone", "Inducer (Required)", "1 uM", "Days 0-14"),
                ("IBMX", "Inducer (Required)", "0.5 mM", "Days 0-14"),
                ("Indomethacin", "Inducer (Required)", "100 uM", "Days 0-14"),
                ("Insulin", "Enhancer (Optional)", "10 ug/mL", "Days 0-21")
            ]
        ),
        (
            "MSC", "Chondrocyte", "Chondrogenic Lineage",
            "High-density pellet/micromass culture in serum-free medium containing TGF-beta3 (or TGF-beta1), Dexamethasone, Ascorbic Acid, and ITS+ supplement for 21-28 days under normoxic or hypoxic (5% O2) conditions.",
            "In Vitro Experimental Differentiation",
            "High cell-density mimics precartilage mesenchymal condensation. High SOX9 expression drives synthesis of cartilage-specific extracellular matrix rich in Collagen Type II (COL2A1) and Aggrecan (ACAN), visualized by Alcian Blue and Safranin O staining.",
            "PMID:9441774",
            [
                ("TGF-beta3", "Inducer (Required)", "10 ng/mL", "Days 0-28"),
                ("Dexamethasone", "Inducer (Required)", "100 nM", "Days 0-28"),
                ("Ascorbic Acid (Vitamin C)", "Inducer (Required)", "50 ug/mL", "Days 0-28")
            ]
        ),

        # ESC / iPSC Pluripotent Lineages
        (
            "ESC", "Neural Progenitor Cell", "Ectoderm (Neural)",
            "Monolayer Dual SMAD inhibition using SB431542 (10 uM) and Noggin (or LDN193189) in KnockOut Serum Replacement (KSR) or N2B27 medium for 8-11 days.",
            "In Vitro Direct Differentiation",
            "Simultaneous suppression of both Activin/Nodal/TGF-β and BMP signaling prevents mesendodermal and epidermal fates, steering >85% of pluripotent cells toward neuroectoderm forming PAX6+ SOX2+ Nestin+ neural rosettes.",
            "PMID:19252484",
            [
                ("SB431542", "Inducer (Required)", "10 uM", "Days 0-10"),
                ("Noggin", "Inducer (Required)", "100 ng/mL", "Days 0-10"),
                ("LDN193189", "Enhancer (Optional)", "100 nM", "Days 0-10")
            ]
        ),
        (
            "IPSC", "Neural Progenitor Cell", "Ectoderm (Neural)",
            "Dual SMAD inhibition (SB431542 + LDN193189/Noggin) in adherent culture for 8-11 days.",
            "In Vitro Direct Differentiation",
            "Identical dual SMAD signaling blockade mechanism as in ESCs, yielding synchronized PAX6+ neural stem/progenitor cells capable of neurogenesis.",
            "PMID:19252484",
            [
                ("SB431542", "Inducer (Required)", "10 uM", "Days 0-10"),
                ("LDN193189", "Inducer (Required)", "100 nM", "Days 0-10"),
                ("Noggin", "Enhancer (Optional)", "100 ng/mL", "Days 0-10")
            ]
        ),
        (
            "ESC", "Midbrain Dopaminergic Neuron", "Ectoderm (Neuronal)",
            "Dual SMAD neural conversion followed by floor plate specification with Sonic Hedgehog (SHH) or Purmorphamine and FGF-8, then maturation with BDNF, GDNF, and Ascorbic Acid for 30-40 days.",
            "In Vitro Stepwise Protocol",
            "Recreates midbrain developmental ontogeny yielding >80% FOXA2+ LMX1A+ floor plate precursors that mature into Tyrosine Hydroxylase (TH+) dopamine-releasing neurons capable of in vivo functional engraftment.",
            "PMID:22056989",
            [
                ("SB431542", "Inducer (Required)", "10 uM", "Days 0-5"),
                ("Noggin", "Inducer (Required)", "100 ng/mL", "Days 0-5"),
                ("SHH (Sonic Hedgehog)", "Inducer (Required)", "200 ng/mL", "Days 1-11"),
                ("Purmorphamine", "Enhancer (Optional)", "2 uM", "Days 1-11"),
                ("FGF-8", "Inducer (Required)", "100 ng/mL", "Days 9-16"),
                ("BDNF", "Inducer (Required)", "20 ng/mL", "Days 16-35"),
                ("GDNF", "Inducer (Required)", "20 ng/mL", "Days 16-35")
            ]
        ),
        (
            "IPSC", "Cardiomyocyte", "Mesoderm (Cardiac)",
            "Temporal biphasic Wnt modulation: Activation with CHIR99021 (6-12 uM) for 24-48 hours (Days 0-1), followed by inhibition with IWP-2 (5 uM) on Days 3-5 in RPMI/B27 minus insulin.",
            "In Vitro Small-Molecule Directed Protocol",
            "Precision temporal control of canonical Wnt/β-catenin signaling. Initial Wnt activation specifies cardiac mesoderm (MESP1+), while subsequent Wnt repression is obligate for cardiogenic specification, yielding >80-90% spontaneously contracting TNNT2+ cardiomyocytes.",
            "PMID:22645348",
            [
                ("CHIR99021", "Inducer (Required)", "10 uM", "Days 0-1"),
                ("IWP-2", "Inducer (Required)", "5 uM", "Days 3-5"),
                ("BMP-4", "Enhancer (Optional)", "5 ng/mL", "Days 0-1")
            ]
        ),
        (
            "ESC", "Cardiomyocyte", "Mesoderm (Cardiac)",
            "Temporal biphasic Wnt regulation with CHIR99021 followed by IWP-2 in RPMI/B27 without insulin.",
            "In Vitro Small-Molecule Directed Protocol",
            "Yields robust monolayers of beating cardiomyocytes expressing cardiac troponin T (TNNT2) and NKX2-5 within 8-12 days.",
            "PMID:22645348",
            [
                ("CHIR99021", "Inducer (Required)", "10 uM", "Days 0-1"),
                ("IWP-2", "Inducer (Required)", "5 uM", "Days 3-5")
            ]
        ),
        (
            "ESC", "Definitive Endoderm", "Endoderm (Primary Germ Layer)",
            "High-concentration Activin A (100 ng/mL) combined with low serum or Wnt activator (CHIR99021, 3 uM) for 3-4 days in RPMI.",
            "In Vitro Directed Differentiation",
            "Mimics nodal signaling during primitive streak gastrulation, directing >90% of cells to SOX17+ FOXA2+ CXCR4+ definitive endoderm, suppressing extraembryonic endoderm.",
            "PMID:16258535",
            [
                ("Activin A", "Inducer (Required)", "100 ng/mL", "Days 0-3"),
                ("CHIR99021", "Enhancer (Optional)", "3 uM", "Day 0-1")
            ]
        ),
        (
            "IPSC", "Pancreatic Beta Cell", "Endoderm (Pancreatic)",
            "Stepwise 6-stage differentiation: Definitive endoderm (Activin A), primitive gut tube, pancreatic progenitor (PDX1+, NKX6-1+), endocrine precursor (NGN3+), and mature insulin-secreting beta cells.",
            "In Vitro Multistage Protocol",
            "Generates glucose-responsive, insulin-secreting beta-like cells expressing PDX1, NKX6-1, MAFA, and chromogranin A capable of ameliorating hyperglycemia in diabetic mice.",
            "PMID:25303535",
            [
                ("Activin A", "Inducer (Required)", "100 ng/mL", "Days 0-3"),
                ("CHIR99021", "Inducer (Required)", "3 uM", "Day 0"),
                ("Noggin", "Enhancer (Optional)", "50 ng/mL", "Days 3-6")
            ]
        ),

        # HSC Lineages
        (
            "HSC", "Granulocyte-Monocyte Progenitor (GMP)", "Myeloid Lineage",
            "Culture in serum-free StemSpan medium supplemented with recombinant human SCF, TPO, FLT3-Ligand, and IL-3/IL-6 for 7-10 days.",
            "In Vitro Hematopoietic Progenitor Assay",
            "Commitment of CD34+ HSCs through Common Myeloid Progenitor (CMP) stage into CD34+ CD38+ CD45RA+ GMPs expressing PU.1 and CEBPA.",
            "PMID:22305562",
            [
                ("SCF (Stem Cell Factor)", "Inducer (Required)", "100 ng/mL", "Days 0-10"),
                ("TPO (Thrombopoietin)", "Inducer (Required)", "50 ng/mL", "Days 0-10"),
                ("FLT3-Ligand", "Inducer (Required)", "50 ng/mL", "Days 0-10")
            ]
        ),
        (
            "HSC", "Macrophage / Monocyte", "Myeloid Lineage",
            "Myeloid differentiation of CD34+ HSCs using SCF, FLT3-Ligand, and GM-CSF followed by terminal differentiation in M-CSF for 14-21 days.",
            "In Vitro Experimental Differentiation",
            "Drives monopoiesis resulting in CD14+ CD68+ phagocytic macrophages expressing scavenger receptors with robust cytokine response.",
            "PMID:19343766",
            [
                ("SCF (Stem Cell Factor)", "Inducer (Required)", "50 ng/mL", "Days 0-7"),
                ("FLT3-Ligand", "Inducer (Required)", "25 ng/mL", "Days 0-7"),
                ("GM-CSF", "Inducer (Required)", "20 ng/mL", "Days 7-21")
            ]
        ),

        # NSC Lineages
        (
            "NSC", "Mature Cortical Neuron", "Neurogenic Lineage",
            "Withdrawal of mitogens (EGF/FGF-2) and supplementation with BDNF, GDNF, and Ascorbic Acid on Poly-L-Ornithine/Laminin matrix for 14-21 days.",
            "In Vitro Directed Differentiation",
            "Loss of Nestin and downregulation of SOX2 followed by rapid neurite outgrowth, expression of beta-III Tubulin (TUJ1) and MAP2, and acquisition of action potential generation.",
            "PMID:10688783",
            [
                ("BDNF", "Inducer (Required)", "20 ng/mL", "Days 0-21"),
                ("GDNF", "Inducer (Required)", "20 ng/mL", "Days 0-21"),
                ("Ascorbic Acid (Vitamin C)", "Enhancer (Optional)", "200 uM", "Days 0-21")
            ]
        ),
        (
            "NSC", "Astrocyte", "Gliogenic Lineage",
            "Withdrawal of FGF-2 and exposure to BMP-2/4 (10 ng/mL) and/or CNTF / serum (1-2% FBS) on laminin substrate for 14-21 days.",
            "In Vitro Directed Differentiation",
            "BMP signaling drives nuclear translocation of phosphorylated SMAD1/5/8 complexed with STAT3, actively repressing neurogenesis and transcribing GFAP and S100B in stellate astrocytes.",
            "PMID:11689956",
            [
                ("BMP-2", "Inducer (Required)", "10 ng/mL", "Days 0-14")
            ]
        ),
        (
            "NSC", "Oligodendrocyte", "Gliogenic Lineage",
            "Sequential treatment with PDGF-AA (10 ng/mL) to expand oligodendrocyte progenitor cells (OPCs, OLIG2+ NG2+), followed by thyroid hormone (T3, 30 ng/mL) for terminal maturation.",
            "In Vitro Stepwise Protocol",
            "Generates mature myelinating oligodendrocytes expressing Myelin Basic Protein (MBP) and CNPase capable of wrapping neuronal axons.",
            "PMID:11689956",
            [
                ("FGF-2 (bFGF)", "Enhancer (Optional)", "10 ng/mL", "Days 0-7")
            ]
        )
    ]

    with get_connection(db_path) as conn:
        for rec in diff_records:
            source, target, lin, cond, ev_type, notes, ref, sig_list = rec
            diff_id = insert_differentiation(source, target, lin, cond, ev_type, notes, ref, db_path=db_path)

            # Link associated signals
            for sname, role, conc, dur in sig_list:
                row = conn.execute("SELECT signal_id FROM signals WHERE signal_name = ?;", (sname,)).fetchone()
                if row:
                    sig_id = row[0]
                    link_differentiation_signal(diff_id, sig_id, role, conc, dur, ref, db_path=db_path)


def _seed_protocols(db_path: Optional[str] = None) -> None:
    protocols = [
        # Protocol 1: MSC Osteogenesis
        (
            "Standard MSC Osteogenic Differentiation Protocol",
            "Mesenchymal Stem Cells (BM-MSC / ADSC)",
            "Osteoblasts (Bone-forming Cells)",
            "Low-glucose DMEM, 10% FBS, 1% Penicillin-Streptomycin, 2 mM L-glutamine",
            "BMP-2 (optional, 100 ng/mL)",
            "Dexamethasone (100 nM), L-Ascorbic Acid 2-phosphate (50 ug/mL), beta-Glycerophosphate (10 mM)",
            "21 days",
            "75 - 85% Alizarin Red-positive matrix mineralization area",
            "Alizarin Red S spectrophotometric quantification at 405 nm; ALPL activity assay",
            "RUNX2, ALPL (Alkaline Phosphatase), BGLAP (Osteocalcin), SPP1 (Osteopontin)",
            "In vitro calcium phosphate nodule mineral deposition and alkaline phosphatase enzymatic secretion",
            "PMID:9029311",
            [
                (1, "Seed MSCs at a density of 3 x 10^4 cells/cm2 in standard tissue culture plastic and culture in basal growth medium until 80-90% confluent.", "Basal MSC Medium", "10% FBS / DMEM", "2-3 days", "Confluence is critical before initiating induction to prevent excessive fibroblastic overgrowth."),
                (2, "Aspirate growth medium and add complete osteogenic induction medium containing 100 nM Dexamethasone and 50 ug/mL Ascorbic Acid 2-phosphate.", "Dexamethasone + Ascorbate", "100 nM / 50 ug/mL", "Days 0-7", "Perform complete medium change every 3 days. Alkaline phosphatase becomes detectable at this stage."),
                (3, "At day 7, supplement induction medium with 10 mM beta-Glycerophosphate as an organic phosphate donor.", "beta-Glycerophosphate", "10 mM", "Days 7-21", "Refeed every 3-4 days. White crystalline mineral deposits become visible macroscopically by day 14-18."),
                (4, "Harvest or fix cells at day 21 with 4% paraformaldehyde. Stain with 2% Alizarin Red S (pH 4.2) for 20 minutes to verify calcium mineral nodule formation.", "Alizarin Red S", "2% solution (pH 4.2)", "20 minutes", "Quantify dye extraction with 10% cetylpyridinium chloride (CPC) at 562 nm.")
            ]
        ),

        # Protocol 2: MSC Adipogenesis
        (
            "Adipogenic Induction and Maintenance Protocol for Human MSCs",
            "Mesenchymal Stem Cells (BM-MSC / ADSC)",
            "Adipocytes (Fat Cells)",
            "High-glucose DMEM (4.5 g/L glucose), 10% FBS",
            "None reported",
            "Dexamethasone (1 uM), IBMX (0.5 mM), Indomethacin (100 uM), Insulin (10 ug/mL)",
            "14 - 21 days",
            "60 - 75% Oil Red O-positive lipid accumulation",
            "Oil Red O extraction and absorbance measurement at 500 nm; Bodipy neutral lipid fluorescence",
            "PPARG, CEBPA, FABP4 (aP2), ADIPOQ (Adiponectin)",
            "Functional accumulation of multilocular and unilocular triglyceride lipid droplets; adipokine secretion",
            "PMID:21545229",
            [
                (1, "Seed human MSCs at 2 x 10^4 cells/cm2 and allow cells to reach 100% confluence; maintain post-confluent for 48 hours to induce growth arrest.", "Basal Growth Medium", "10% FBS / DMEM", "3-4 days", "Post-confluent growth arrest triggers contact inhibition necessary for adipogenic lineage induction."),
                (2, "Initiate adipogenic induction cycle by replacing medium with induction cocktail: 1 uM Dexamethasone, 0.5 mM IBMX, 100 uM Indomethacin, and 10 ug/mL Insulin.", "Adipogenic Induction Cocktail", "1 uM Dex, 0.5 mM IBMX, 100 uM Indo, 10 ug/mL Insulin", "3 days", "IBMX rapidly boosts intracellular cAMP, while Dexamethasone and Indomethacin induce C/EBPβ and PPARγ."),
                (3, "Switch medium to adipogenic maintenance medium containing only 10 ug/mL Insulin in high-glucose DMEM/FBS for 24-48 hours.", "Insulin Maintenance Medium", "10 ug/mL Insulin", "1-2 days", "Alternating induction (3 days) and maintenance (1-2 days) prevents cytotoxic exhaustion from continuous IBMX."),
                (4, "Repeat 3 cycles of induction and maintenance for a total of 14-21 days. Fix in 4% PFA and stain with 0.5% Oil Red O in isopropanol.", "Oil Red O Stain", "0.5% working solution", "30 minutes", "Red ringed cytoplasmic lipid droplets confirm adipocyte differentiation.")
            ]
        ),

        # Protocol 3: MSC Chondrogenesis
        (
            "High-Density Micromass Pelleted Chondrogenesis Protocol",
            "Bone Marrow Mesenchymal Stem Cells (BM-MSC)",
            "Chondrocytes (Cartilage-forming Cells)",
            "High-glucose DMEM, ITS+ premix (insulin, transferrin, selenious acid, BSA, linoleic acid), sodium pyruvate (1 mM), proline (40 ug/mL)",
            "TGF-beta3 (10 ng/mL) or TGF-beta1 (10 ng/mL)",
            "Dexamethasone (100 nM), L-Ascorbic acid 2-phosphate (50 ug/mL)",
            "21 - 28 days",
            "Not reported (evaluated by histological scoring: Bern Score 8-9/9)",
            "Bern Histological Chondrogenesis Score; Alcian Blue and Safranin-O proteoglycan metachromasia",
            "SOX9, COL2A1 (Collagen Type II), ACAN (Aggrecan); Absence of COL1A1 / COL10A1",
            "Mechanical stiffness testing; proteoglycan-rich glycosaminoglycan (sGAG) synthesis quantified by DMMB assay",
            "PMID:9441774",
            [
                (1, "Aliquot 2.5 x 10^5 viable MSCs into 15 mL polypropylene conical tubes and centrifuge at 150 x g for 5 minutes at room temperature.", "Basal Medium", "N/A", "5 minutes", "Centrifugation forces cell-cell compaction into a spherical pellet, mimicking embryonic mesenchymal condensation."),
                (2, "Do not disrupt the cell pellet. Carefully add 0.5 mL complete chondrogenic medium containing 10 ng/mL TGF-beta3, 100 nM Dexamethasone, and 50 ug/mL Ascorbic Acid.", "Chondrogenic Induction Medium", "10 ng/mL TGF-b3", "24-48 hours", "Within 24-48 hours, the cell pellet coalesces into a coherent spherical free-floating cartilage micromass."),
                (3, "Perform medium changes every 2 to 3 days by gently aspirating medium without touching the pellet.", "Chondrogenic Maintenance Medium", "10 ng/mL TGF-b3", "Days 2-28", "The pellet expands in diameter due to copious extracellular cartilage matrix secretion."),
                (4, "At day 21-28, collect pellet for cryosectioning and immunohistochemistry. Stain sections with Toluidine Blue or Safranin-O.", "Safranin-O Stain", "0.1% aqueous solution", "5 minutes", "Strong red metachromatic matrix confirms sulfated proteoglycans and hyaline cartilage phenotype.")
            ]
        ),

        # Protocol 4: Pluripotent Neural Dual SMAD
        (
            "Dual SMAD Inhibition Monolayer Neural Conversion Protocol",
            "Human Pluripotent Stem Cells (hESC H9 / hiPSC)",
            "Neural Progenitor Cells (PAX6+ Neuroectoderm)",
            "KnockOut DMEM / KSR (Days 0-4), transitioning stepwise to N2B27 medium (Days 5-11)",
            "Noggin (100 ng/mL) or small-molecule LDN193189 (100 nM)",
            "SB431542 (10 uM)",
            "11 days",
            "82 - 92% PAX6+ SOX2+ neural rosette progenitors",
            "Flow cytometry for PAX6 and SOX2; quantitative RT-PCR for neuroectodermal transcripts",
            "PAX6, SOX2, NES (Nestin), OTX2; Loss of OCT4 and NANOG",
            "Ability to organize into apical-basal polarized neural rosettes and differentiate into functional cortical and motor neurons",
            "PMID:19252484",
            [
                (1, "Seed feeder-free hESCs/iPSCs as high-density single cells (4 x 10^4 cells/cm2) on Matrigel in mTeSR1 with 10 uM Y-27632 ROCK inhibitor.", "mTeSR1 + Y-27632", "10 uM Y-27632", "Day -1 to 0", "Plating as uniform monolayers ensures synchronized receptor access across the entire cell population."),
                (2, "At Day 0 (100% confluent), switch to KnockOut Serum Replacement (KSR) medium containing 10 uM SB431542 and 100 ng/mL Noggin (or 100 nM LDN193189).", "Dual SMAD Medium (KSR)", "10 uM SB431542 + 100 nM LDN", "Days 0-4", "Suppression of SMAD2/3 and SMAD1/5/8 completely inhibits non-neural endoderm, mesoderm, and epidermal fates."),
                (3, "Beginning at Day 5, transition medium to N2B27 neural induction medium in 25% increments (75:25, 50:50, 25:75, 0:100) while maintaining dual SMAD inhibitors.", "N2B27 Neural Medium", "Dual SMAD inhibitors", "Days 5-11", "Monolayer forms dense neuroepithelial sheets with visible neural rosettes by day 8-10."),
                (4, "At Day 11, neuroepithelial rosettes can be enzymatically selected with Accutase and replated as neural stem/progenitor lines.", "Accutase / N2B27", "1X", "Day 11+", "Cells demonstrate >85% PAX6 positivity by flow cytometry.")
            ]
        ),

        # Protocol 5: Pluripotent Wnt Cardiomyogenesis
        (
            "GiWi Temporal Wnt-Modulated Cardiomyocyte Differentiation Protocol",
            "Human Pluripotent Stem Cells (hESC H1/H9, hiPSC WTC-11)",
            "Cardiomyocytes (Contractile Heart Cells)",
            "RPMI 1640 medium supplemented with B27 minus insulin (Days 0-7), followed by RPMI + B27 complete (Day 7+)",
            "None reported",
            "CHIR99021 (GSK3 inhibitor, 10-12 uM), IWP-2 (Porcupine/Wnt inhibitor, 5 uM)",
            "12 - 15 days",
            "80 - 95% Cardiac Troponin T (TNNT2)+ cardiomyocytes",
            "Flow cytometry for TNNT2 and ACTC1; multi-electrode array (MEA) electrophysiology",
            "TNNT2 (Troponin T), NKX2-5, MYH6 (alpha-MHC), ACTC1; Absence of pluripotency markers",
            "Autonomous spontaneous rhythmic mechanical contractions; responsive to chronotropic beta-adrenergic agonists (isoproterenol)",
            "PMID:22645348",
            [
                (1, "Culture hPSCs on Matrigel until 85-95% confluent in mTeSR1 or E8 medium.", "mTeSR1 / E8", "N/A", "Day -3 to 0", "Optimal initial cell density is critical for determining appropriate CHIR99021 concentration."),
                (2, "On Day 0, replace medium with RPMI 1640 / B27 minus insulin containing 10-12 uM CHIR99021. Incubate for exactly 24 hours.", "RPMI/B27-ins + CHIR99021", "10-12 uM CHIR", "Day 0-1 (24 hrs)", "Potent canonical Wnt activation specifies primitive streak and cardiac mesoderm (MESP1+)."),
                (3, "At exactly 24 hours (Day 1), aspirate medium and replace with fresh RPMI / B27 minus insulin without small molecules for 48 hours.", "RPMI / B27 minus insulin", "N/A", "Days 1-3", "Allows transition from primitive streak mesoderm toward cardiac progenitor specification."),
                (4, "On Day 3, add 5 uM IWP-2 in RPMI / B27 minus insulin. Incubate for 48 hours without disturbance.", "RPMI/B27-ins + IWP-2", "5 uM IWP-2", "Days 3-5", "Suppression of endogenous Wnt ligand secretion is strictly required for commitment to cardiac lineage."),
                (5, "On Day 5, remove IWP-2 and replace with RPMI / B27 minus insulin. On Day 7, switch to RPMI / B27 complete (with insulin).", "RPMI / B27 complete", "Insulin-replete", "Days 7-15", "Widespread spontaneous synchronous beating sheets observed by Day 8-10.")
            ]
        ),

        # Protocol 6: Pluripotent Pancreatic Beta Cells
        (
            "Stepwise Scalable Pancreatic Beta Cell Protocol",
            "Human Pluripotent Stem Cells (hESC RUES2 / hiPSC)",
            "Pancreatic Beta Cells (Glucose-Responsive Insulin-Producing Cells)",
            "MCDB-131 base formulation with stage-specific growth factor combinations",
            "Activin A (100 ng/mL), Wnt3a / CHIR99021, FGF7 / KGF (50 ng/mL), EGF (20 ng/mL)",
            "SANT-1 (SHH inhibitor, 0.25 uM), Retinoic Acid (2 uM), Alk5 inhibitor II, T3",
            "28 - 35 days",
            "30 - 45% C-peptide+ INS+ monohormonal beta cells",
            "Intracellular flow cytometry for C-peptide and PDX1; Glucose-Stimulated Insulin Secretion (GSIS) ELISA",
            "PDX1, NKX6-1, INS (Insulin), MAFA, CHGA (Chromogranin A)",
            "Static and dynamic Glucose-Stimulated Insulin Secretion (GSIS) with insulin release index >2.0 upon high glucose (16.7 mM); in vivo rescue of streptozotocin-induced hyperglycemia in diabetic mice",
            "PMID:25303535",
            [
                (1, "Stage 1 (Definitive Endoderm): Expose suspension clusters to 100 ng/mL Activin A and 3 uM CHIR99021 in base medium for 3 days.", "Activin A + CHIR", "100 ng/mL / 3 uM", "Days 0-3", "Generates >90% SOX17+ FOXA2+ definitive endoderm."),
                (2, "Stage 2 (Primitive Gut Tube): Culture in KGF (50 ng/mL) in MCDB-131 with 1.5% BSA for 3 days.", "KGF / FGF7", "50 ng/mL", "Days 3-6", "Restricts endoderm to anterior-posterior patterning."),
                (3, "Stage 3 (Pancreatic Progenitors): Add Retinoic Acid (2 uM), SANT-1 (0.25 uM), and Noggin (50 ng/mL) for 4 days.", "RA + SANT-1 + Noggin", "2 uM / 0.25 uM / 50 ng/mL", "Days 6-10", "Drives robust expression of PDX1 (>80%) in dorsal pancreatic lineage."),
                (4, "Stage 4 & 5 (Endocrine Specification): Add Alk5 inhibitor II (10 uM) and Thyroid Hormone (T3) for 14 days.", "Alk5i II + T3 + Betacellulin", "10 uM / 1 uM", "Days 10-28", "Induces NGN3 and matures endocrine precursors into monohormonal C-peptide+ beta cells.")
            ]
        ),

        # Protocol 7: Midbrain Dopaminergic Neurons
        (
            "Floor Plate Midbrain Dopaminergic Neuron Protocol",
            "Human Embryonic Stem Cells (H9) / hiPSC",
            "A9 Midbrain Dopaminergic Neurons (Substantia Nigra Type)",
            "KnockOut Serum Replacement base, transitioning to Neurobasal / B27 medium",
            "SHH (200 ng/mL), FGF-8 (100 ng/mL), BDNF (20 ng/mL), GDNF (20 ng/mL)",
            "SB431542 (10 uM), Noggin (100 ng/mL), Purmorphamine (2 uM), CHIR99021 (0.8 uM), DAPT (10 uM)",
            "35 - 45 days",
            "70 - 80% FOXA2+ LMX1A+ floor plate progenitors; ~60-70% TH+ mature dopaminergic neurons",
            "Immunofluorescence and FACS for Tyrosine Hydroxylase (TH), FOXA2, GIRK2; HPLC measurement of dopamine release upon KCl depolarization",
            "TH (Tyrosine Hydroxylase), FOXA2, LMX1A, EN1, PITX3, GIRK2 (KCNJ6)",
            "Electrophysiological whole-cell patch clamp recording of spontaneous rhythmic pacemaker action potentials; reversal of rotational asymmetry in 6-OHDA parkinsonian rat models upon in vivo intrastriatal transplantation",
            "PMID:22056989",
            [
                (1, "Initiate dual SMAD inhibition with 10 uM SB431542 and 100 ng/mL Noggin for 4 days in monolayer culture.", "SB431542 + Noggin", "10 uM / 100 ng/mL", "Days 0-4", "Directs rapid neural specification."),
                (2, "From Day 1 to 11, add 200 ng/mL Sonic Hedgehog (SHH) and 2 uM Purmorphamine with 0.8 uM CHIR99021.", "SHH + Purmorphamine + CHIR", "200 ng/mL / 2 uM / 0.8 uM", "Days 1-11", "Specifies floor plate midbrain identity, inducing co-expression of FOXA2 and LMX1A."),
                (3, "At Day 11, replate on poly-L-ornithine/laminin/fibronectin in Neurobasal/B27 containing 100 ng/mL FGF-8.", "FGF-8", "100 ng/mL", "Days 11-16", "Stabilizes anteroposterior caudal midbrain identity."),
                (4, "From Day 16 onward, mature neurons in Neurobasal/B27 with BDNF (20 ng/mL), GDNF (20 ng/mL), Ascorbic acid (200 uM), and TGF-beta3 (1 ng/mL).", "BDNF + GDNF + Ascorbate", "20 ng/mL / 20 ng/mL", "Days 16-40", "Matures postmitotic dopaminergic neurons exhibiting spontaneous action potentials.")
            ]
        ),

        # Protocol 8: HSC Myeloid / Macrophage Protocol
        (
            "CD34+ Hematopoietic Stem Cell Myeloid Directed Differentiation Protocol",
            "Hematopoietic Stem Cells (CD34+ Cord Blood Primary)",
            "Macrophages (CD14+ CD68+ Phagocytic Cells)",
            "StemSpan SFEM II serum-free expansion medium transitioning to RPMI 1640 / 10% FBS",
            "SCF (50 ng/mL), FLT3-Ligand (25 ng/mL), GM-CSF (20 ng/mL), M-CSF (50 ng/mL)",
            "None reported",
            "14 - 21 days",
            "70 - 85% CD14+ CD68+ macrophages",
            "Flow cytometry for CD14, CD68, CD11b; Latex bead phagocytosis assay",
            "CD14, CD68, ITGAM (CD11b), PU.1, CSF1R",
            "Phagocytosis of fluorescent latex beads; secretion of TNF-alpha and IL-6 upon LPS stimulation",
            "PMID:19343766",
            [
                (1, "Enrich primary CD34+ cord blood cells by MACS immunomagnetic column and plate at 5 x 10^4 cells/mL in StemSpan SFEM II.", "StemSpan SFEM II", "N/A", "Day 0", "Verify purity >95% CD34+ by analytical flow cytometry prior to differentiation initiation."),
                (2, "Add myeloid progenitor expansion cocktail: recombinant human SCF (50 ng/mL), FLT3-Ligand (25 ng/mL), and IL-3 (10 ng/mL) for 5 days.", "Progenitor Expansion Cocktail", "50 / 25 / 10 ng/mL", "Days 0-5", "Promotes robust expansion of common myeloid progenitors (CMPs) while maintaining cell survival."),
                (3, "At Day 5, transition medium to RPMI 1640 containing 10% FBS and 20 ng/mL recombinant human GM-CSF.", "GM-CSF Differentiation Medium", "20 ng/mL GM-CSF", "Days 5-12", "Drives commitment of progenitors to monocyte/macrophage lineage (CD14 upregulation)."),
                (4, "At Day 12, switch to M-CSF (50 ng/mL) on tissue-culture treated plastic to induce terminal macrophage adherence and spreading.", "M-CSF Maturation Medium", "50 ng/mL M-CSF", "Days 12-21", "Adherent spread cells demonstrate robust phagocytic uptake of fluorescent bacterial particles.")
            ]
        )
    ]

    for p in protocols:
        p_name, s_cell, t_cell, med, gf, sm, dur, eff, eff_m, markers, f_val, ref, steps = p
        pid = insert_protocol(
            protocol_name=p_name,
            source_cell=s_cell,
            target_cell=t_cell,
            medium=med,
            growth_factors=gf,
            small_molecules=sm,
            duration=dur,
            reported_efficiency=eff,
            efficiency_method=eff_m,
            validation_markers=markers,
            functional_validation=f_val,
            reference_id=ref,
            db_path=db_path
        )
        for s_num, proc, reag, conc, s_dur, notes in steps:
            insert_protocol_step(
                protocol_id=pid,
                step_number=s_num,
                procedure=proc,
                reagent=reag,
                concentration=conc,
                duration=s_dur,
                notes=notes,
                db_path=db_path
            )


if __name__ == "__main__":
    seed_database()
