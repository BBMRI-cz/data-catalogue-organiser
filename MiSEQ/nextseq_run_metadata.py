import xml.etree.ElementTree as ET
import json
import PyPDF2
import sys
from datetime import date

#script can be run by command: python nextseq_run_metadata_extraction.py RunParameters.xml RunCompletionStatus.xml RunInfo.xml report.pdf

class RunInfoMMCI:

    def __init__(self):
        self.idMMCI: int = 0            #XML_RunParameters
        self.seqDate: str = ''          #XML_RunParameters
        self.seqPlatform: str = ''      #always "Illumina platform"
        self.seqModel: str = ''         #NextSeq 550
        self.seqMethod: str = ''        #always "Illumina Sequencing"
        #self.avReadDepth: str = '' - data from CGW doesnt include this information, it can be calculated using SAMtools tool with command "samtools depth"
        #self.obsReadLength: str = '' - data from CGW doesnt include this information, it can be calculated using SAMtools tool with command "samtools stats"
        self.obsInsertSize: int = 0     #QC Metrics Report - Trusight Oncology 500 (pdf) - FILE PER ONE SAMPLE FROM ANALYSIS
        self.percentageQ30: int = ''  #available in InterOp file possible to open only in BaseSpace, cannot be extracted
        self.percentageTR20: str = ''  #this number is not relevant for MMCI
        self.clusterDensity: float = 0  #XML_RunCompletionStatus
        self.clusterPF: float = 0       #XML_RunCompletionStatus
        self.estimatedYield: float = 0  #XML_RunCompletionStatus
        self.errorDescription: str = '' #XML_RunCompletionStatus
        self.numLanes: int = 0          #XML_RunParameters
        self.flowcellID: str = ''       #XML_RunInfo

def find_el_in_runparam(tree1, run):          #this function extracts run parameters from file "RunParameters"
    for element in tree1.iter("RunParameters"):
        run.idMMCI = "nxt_" + element.find("RunNumber").text
        run_date = element.find("RunStartDate").text
        year = 2000 + int(run_date[:2])  # prekonvertovanie roku do celého čísla
        month = int(run_date[2:4])
        day = int(run_date[4:])
        d = date(year, month, day)
        isoformat = d.isoformat()
        run.seqDate = isoformat
        run.seqPlatform = "Illumina platform"
        run.seqMethod = "Illumina Sequencing"
        run.seqModel = "NextSeq 550"
    for element in tree1.iter("Setup"):
        run.numLanes = element.find("NumLanes").text
    return run


def find_el_in_runcomplstatus(tree2, run):   #this function extracts run parameters from file RunCompletionStatus
    for element in tree2.iter("RunCompletionStatus"):
        run.clusterDensity = element.find("ClusterDensity").text
        run.clusterPF = element.find("ClustersPassingFilter").text
        run.estimatedYield = element.find("EstimatedYield").text
        run.errorDescription = element.find("ErrorDescription").text
    return run


def find_el_in_runinfo(tree3, run):
    for element in tree3.iter("Run"):
        run.flowcellID = element.find("Flowcell").text
    return run

def between(value, a, b):
    pos_a = value.find(a)
    if pos_a == -1: return ""
    pos_b = value.find(b)
    if pos_b == -1: return ""
    adjust_pos_a = pos_a + len(a)
    if adjust_pos_a >= pos_b: return ""
    return value[adjust_pos_a: pos_b]

def find_el_in_pdf(pdf_file, run):
    with open(pdf_file, "rb") as file:
        pdfFileReader = PyPDF2.PdfReader(file)
        pages = pdfFileReader.pages[0]
        text = pages.extract_text()
        desired = between(text, "MEDIAN_INSERT_SIZE (bp)", ">= 70")
    run.obsInsertSize = desired
    run.percentageTR20 = "NA"
    run.percentageQ30 = "NI"
    return run


def find_run_metadata(first_source, second_source, third_source, pdf_file):
    run = RunInfoMMCI()
    tree1 = ET.parse(first_source)
    run = find_el_in_runparam(tree1, run)
    tree2 = ET.parse(second_source)
    run = find_el_in_runcomplstatus(tree2, run)
    tree3 = ET.parse(third_source)
    run = find_el_in_runinfo(tree3, run)
    run = find_el_in_pdf(pdf_file, run)
    jsonStr = json.dumps(run.__dict__)
    return jsonStr


if __name__ == "__main__":
    xml_runParameters = sys.argv[1]
    xml_runCompletionStatus = sys.argv[2]
    xml_runInfo = sys.argv[3]
    pdf_file = sys.argv[4]

    data = find_run_metadata(xml_runParameters, xml_runCompletionStatus, xml_runInfo, pdf_file)
    with open('run_metadata.json', 'w') as outfile:
        outfile.write(data)
