from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.views.vitimas_view import VitimaEdit, create_vitima, delete_vitima, list_vitimas, update_vitima
from src.views.sites_view import list_iml, list_iml_for_export
router = APIRouter()
from openpyxl import Workbook
from io import BytesIO
from fastapi.responses import FileResponse


class Vitima(BaseModel):
    datadofato: str
    diah: str
    horario: str
    turno: str
    nome: str
    idade: int
    racacor1: str
    estciv2: str
    bairro: str
    rua_beco_travessa_estrada_ramal: str
    endcomplemento: str
    tipoarma1: str
    tipoarma2: str
    loclesao1: str
    loclesao2: str
    loclesao3: str
    hospitalizacao: str
    violsexual: str
    latrocinio: str
    zona: str
    localdeocorrencia: str
    presencafilhofamiliar: str
    gestacao: str
    filhosdescrever: int
    sites: Optional[List[UUID]] = []


@router.post("/vitimas/")
async def create_vitimas_controller(vitima: Vitima):
    return await create_vitima(vitima)


@router.get("/vitimas/")
async def list_tags_controller():
    return await list_vitimas()


# @router.get("/tag/{tag_name}", response_model=Tag)
# async def list_one_tag_controller(tag_name: str):
#     return await list_one_tag(tag_name)


@router.patch("/vitimas/{vitima_id}")
async def update_vitima_controller(vitima_id, item: dict):
    return await update_vitima(vitima_id, item)


@router.delete("/vitimas/{vitima_id}")
async def delete_vitimas_controller(vitima_id: str):
    return await delete_vitima(vitima_id)

headers = ["numero1", "registro_fvs_do", "naocapturado", "homicidio", "numerodo", "datadofato",
           "diah", "diasemh", "mesh", "anoh", "horario", "turno", "nome", "idade", "racacor1", "estciv2",
           "esc2", "bairro", "zona", "rua/beco/travessa/estrada/ramal", "endcomplemento",
           "local_desova_corpo", "X_Lati", "Y_Long", "precisao_local_classificacao", "coordenadas_derivam",
           "cid10cod4final", "cid10cod4finaltexto", "tipoarma1", "tipoarma2", "loclesao1", "loclesao2",
           "loclesao3", "localdaslesoes", "numerodelesoes", "possivelfemin", "hospitalizacao",
           "vitusudrogilicita", "relacaotraf", "crimepassion", "violsexual", "usodealcool", "latrocinio",
           "tipoviol", "localdeocorrencia", "presencafilhofamiliar", "situacaorua", "nivsupcomouincomp",
           "represalia trafico", "sexoagressor", "compexcomp", "outrofamconhefam", "compexfam", "excompan",
           "conhecido", "circunsmorte", "gestacao", "puerperio", "filhosdescrever", "menor14anos",
           "maior60anos", "vulnerabil_fisica_mental", "presenca_ascend_descendente",
           "presenca_medida_protet_urgen", "tipo_intimo_naointimo", "inf_bol_ocorrencia_iml_bol",
           "inf_bol_ocorrencia_revisao", "consulta_saj_bol1", "consulta_saj_bol2", "consulta_saj_revisao1",
           "consulta_saj_revisao2", "observacoes", "SITE1", "SITE2", "SITE3", "SITEGEO1", "SITEGEO2",
           "SITEGEO3", "check_30dias"]

def export_to_xlsx(data):
    wb = Workbook()
    ws = wb.active

    ws.append(headers)

    for row in data:
        row_dict = dict(row)
        row_data = [row_dict.get(header, "") for header in headers]
        ws.append(row_data)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output

headers_iml = ["dataEntrada", "horaEntrada", "sexo", "idade", "bairroDaRemocao", "causaMorte"]

def export_to_xlsx_iml(data):
    wb = Workbook()
    ws = wb.active

    ws.append(headers)

    for row in data:
        row_dict = dict(row)
        row_data = [row_dict.get(header, "") for header in headers_iml]
        ws.append(row_data)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output

from fastapi.responses import StreamingResponse


@router.get("/export-xlsx")
async def export_xlsx():
    try:
        vitimas_data = await list_vitimas()

        output = export_to_xlsx(vitimas_data)

        return StreamingResponse(content=output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=vitimas.xlsx"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/iml/export-xlsx")
async def export_iml_xlsx():
    try:
        iml_data = await list_iml_for_export()

        output = export_to_xlsx_iml(iml_data)

        return StreamingResponse(content=output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=iml.xlsx"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
