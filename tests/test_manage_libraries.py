import pytest
from organiser.manage_libraries import LibrariesManager
import os
import shutil

TEST_LIBRARY_FOLDER = os.path.join(os.path.dirname(__file__), "test_libraries")
TEST_DESTINATION_RUN = os.path.join(os.path.dirname(__file__), "test_destination_for_copy", "2020", "MiSEQ", "00000",
                                    "2020_M00000_0000_00000000-00000")
SPECIAL_SAMPLE_SHEET = os.path.join(os.path.dirname(__file__), "SpecialSampleSheet.csv")


def _move_back_sample_sheets():
    shutil.move(os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"), SPECIAL_SAMPLE_SHEET)
    shutil.move(os.path.join(os.path.dirname(__file__), "OriginalSampleSheet.csv"),
                os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"))


@pytest.fixture()
def use_different_sample_sheet(request):
    shutil.move(os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"),
                os.path.join(os.path.dirname(__file__), "OriginalSampleSheet.csv"))
    shutil.move(SPECIAL_SAMPLE_SHEET, os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"))

    request.addfinalizer(_move_back_sample_sheets)


def test_correct_library_file_selected():
    manager = LibrariesManager(TEST_LIBRARY_FOLDER, os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"),
                               TEST_DESTINATION_RUN, "mmci_predictive_00000000-0000-0000-0000-000000000001")

    assert manager.libraries_path == os.path.join(TEST_LIBRARY_FOLDER, "LibrariesV240126.csv")


def test_correct_data_extracted_from_library_with_panel_in_parameters():
    manager = LibrariesManager(TEST_LIBRARY_FOLDER,
                               os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"),
                               TEST_DESTINATION_RUN,
                               "mmci_predictive_00000000-0000-0000-0000-000000000001")

    results = manager.get_data_from_libraries()

    assert results == {
        "input_amount": "10-25ngr",
        "library_prep_kit": "Accel-Amplicon Plus Panel by Swift Biosciences/IDT",
        "pca_free": False,
        "target_enrichment_kid": "Accel Amplicon Custom Core Kit",
        "umi_present": False,
        "intended_insert_size": 265,
        "intended_read_length": 150,
        "genes": "ALK, APC, ARAF, BRAF, CDKN2A, EGFR, ERBB2, ERBB4, FGFR1, FGFR2, FGFR3, KIT," +
                 " KRAS, MAP2K1, MET, NOTCH1, NRAS, PDGFRA, PIK3CA, PTEN, STK11, TP53*"
    }


def test_correct_data_extracted_from_library_with_manual_panel():
    manager = LibrariesManager(TEST_LIBRARY_FOLDER,
                               os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"),
                               TEST_DESTINATION_RUN,
                               "mmci_predictive_00000000-0000-0000-0000-000000000002")

    results = manager.get_data_from_libraries()

    assert results == {'genes': 'AKT1,ALK,APC,ARAF,BRAF,BRCA1*,BRCA2*,CDKN2A,EGFR,ERBB2,ERBB4,FGFR1,FGFR2,FGFR3,' +
                                'KIT,KRAS,MAP2K1,MET,NOTCH1,NRAS,PDGFRA,PIK3CA,POLE,PTEN,STK11,TP53*',
                       'input_amount': '10-25ngr',
                       'intended_insert_size': 265,
                       'intended_read_length': 151,
                       'library_prep_kit': 'Accel-Amplicon Plus Panel by Swift Biosciences',
                       'pca_free': False,
                       'target_enrichment_kid': 'Accel Amplicon Custom Core Kit',
                       'umi_present': False}


def test_correct_data_extraction_from_library_with_panel_based_on_date(use_different_sample_sheet):
    manager = LibrariesManager(TEST_LIBRARY_FOLDER,
                               os.path.join(TEST_DESTINATION_RUN, "SampleSheet.csv"),
                               TEST_DESTINATION_RUN,
                               "mmci_predictive_00000000-0000-0000-0000-000000000002")

    results = manager.get_data_from_libraries()

    assert results == {'genes': 'AKT1, ALK, APC, AR, ARAF, BAP1, BRAF, BRCA1*, BRCA2*, CDH1, CDKN2A, '
                                'CTNNB1, EGFR, ERBB2*, ESR1*, FBXW7, FGFR2, FGFR3, FOXL2, GNA11, '
                                'GNAQ, GNAS, HRAS, CHEK2, IDH1, KDR, KIT, KRAS*, MAP2K1, MAP2K4, '
                                'MET, MLH1, MTOR, NF1, NOTCH1, NRAS*, PDGFRA, PIK3CA*, POLE, PTEN, '
                                'RB1, RET, SMAD4, SMO, SRC, STK11, TP53*',
                                'input_amount': '100ngr',
                                'intended_insert_size': 200,
                                'intended_read_length': 75,
                                'library_prep_kit': 'KAPA HyperPlus Kits by Roche: '
                                                    'https://w3id.org/fair-genomes/resource/FG_0000127',
                                'pca_free': True,
                                'target_enrichment_kid': 'KAPA HyperChoice',
                                'umi_present': False}
