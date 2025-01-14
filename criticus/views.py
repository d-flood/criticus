import traceback

from django.http import HttpRequest
from django.shortcuts import render

from criticus.py.md2tei import markdown_to_tei as md2tei
from criticus.py.txt2json import convert_text_to_json as txt2json


async def home(request: HttpRequest):
    context = {
        "page": "home",
    }
    return render(request, "index.html", context)


async def plain_text_to_json(request: HttpRequest):
    if request.method == "POST":
        print(request.POST)
        if not request.POST.get("single-ref"):  # convert all or some in file
            try:
                txt2json.convert_text_to_json(
                    filename=request.POST.get("input_file"),
                    output_dir=request.POST.get("output_directory"),
                    convert_all=bool(
                        request.POST.get("all-or-range") == "all_verses_in_file"
                    ),
                    reference_prefix=request.POST.get("unit-prefix"),
                    auto=bool(request.POST.get("ref-prefix", "") == "auto"),
                    verse_from=request.POST.get("range-from"),
                    verse_to=request.POST.get("range-to"),
                    siglum=request.POST.get("siglum"),
                )
                context = {
                    "modal_title": "Success",
                    "modal_text": "Your text file has been converted to JSON files.",
                    "status": "success",
                }
            except Exception as e:
                context = {
                    "modal_title": "Error",
                    "modal_text": f"An error occurred: {e}",
                    "error_text": traceback.format_exc(),
                    "status": "fail",
                }
                print(traceback.format_exc())
        else:  # convert from directly provided text
            try:
                txt2json.convert_single_verse_to_json(
                    text=request.POST.get("input_text"),
                    siglum=request.POST.get("siglum"),
                    reference=request.POST.get("single-ref"),
                    output_dir=request.POST.get("output_directory"),
                )
                context = {
                    "modal_title": "Success",
                    "modal_text": "Your text has been converted to a JSON file.",
                    "status": "success",
                }
            except Exception as e:
                context = {
                    "modal_title": "Error",
                    "modal_text": f"An error occurred: {e}",
                    "error_text": traceback.format_exc(),
                    "status": "fail",
                }
                print(traceback.format_exc())
        return render(request, "_modal.html", context)
    else:  # GET
        context = {
            "page": "txt2json",
        }
        return render(request, "plain_text_to_json.html", context)


async def markdown_to_tei(request: HttpRequest):
    if request.method == "POST":
        print(request.POST)
        try:
            md2tei.convert_md_to_tei(
                md_file=request.POST.get("input_file"),
                xml_file=request.POST.get("output_file"),
                output_format=request.POST.get("format"),
            )
            context = {
                "modal_title": "Success",
                "modal_text": f"Your Markdown file has been converted to TEI XML and saved to {request.POST.get('output_file')}.",
                "status": "success",
            }
        except Exception as e:
            context = {
                "modal_title": "Error",
                "modal_text": f"An error occurred: {e}",
                "error_text": traceback.format_exc(),
                "status": "fail",
            }
            print(traceback.format_exc())
        return render(request, "_modal.html", context)
    # GET
    context = {
        "page": "md2tei",
    }
    return render(request, "markdown_to_tei.html", context)


async def tei_to_json(request: HttpRequest):
    context = {
        "page": "tei2json",
    }
    return render(request, "tei_to_json.html", context)
