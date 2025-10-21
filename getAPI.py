import os, time, csv, requests
from urllib.parse import urlencode

# ==== CẦN ĐIỀN ====
BASE_URL = os.getenv("NBRS_BASE_URL", "https://<gateway-domain>/api/registration")  # ví dụ qua NGSP/LGSP
API_KEY  = os.getenv("NBRS_API_KEY",  "<YOUR_API_KEY>")   # hoặc Bearer token
ORG_CODE = os.getenv("ORG_CODE",      "<MA_CO_QUAN>")     # nếu yêu cầu định danh đơn vị
# ===================

# Theo tài liệu, khối EntInfo có địa chỉ trụ sở HOAdress với CityID/DistrictID/WardID
# CityID Hải Phòng (ví dụ): 31 (tuỳ bảng mã đi kèm môi trường triển khai)
CITY_ID_HAIPHONG = 31  # thay bằng mã chính thức môi trường của bạn

# Endpoint tham khảo (đặt theo tài liệu đơn vị cấp):
# 1) Danh sách DN theo bộ lọc: /enterprises/search
# 2) Chi tiết 1 DN:          /enterprises/{enterprise_code}  (chiTietDoanhNghiep)
# Bạn cần đối chiếu tên endpoint thực tế được cấp.
LIST_ENDPOINT  = f"{BASE_URL}/enterprises/search"
DETAIL_ENDPOINT = f"{BASE_URL}/enterprises/{{enterprise_code}}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    # Một số cổng yêu cầu x-org/x-client headers
    "X-Org-Code": ORG_CODE,
}

def fetch_page(offset=0, limit=1000):
    """
    Gọi danh sách DN theo phân trang.
    Một số triển khai dùng page/pageSize; số khác dùng offset/limit.
    Tham số lọc theo CityID (địa chỉ trụ sở chính).
    """
    payload = {
        "filters": {
            "headOffice": {
                "cityId": CITY_ID_HAIPHONG
            }
        },
        "sort": [{"field": "ENTERPRISE_CODE", "dir": "asc"}],
        "offset": offset,    # hoặc "page": n
        "limit": limit       # hoặc "pageSize": n
    }
    r = requests.post(LIST_ENDPOINT, headers=HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def fetch_detail(enterprise_code: str):
    url = DETAIL_ENDPOINT.format(enterprise_code=enterprise_code)
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    out_file = "doanh_nghiep_HaiPhong.csv"
    fieldnames = [
        "ENTERPRISE_CODE", "ENTERPRISE_GDT_CODE", "NAME", "ENTERPRISE_TYPE_NAME",
        "ENTERPRISE_STATUS_NAME", "FOUNDING_DATE", "LAST_AMEND_DATE",
        "REPRESENTATIVE_FULL_NAME",
        "HO_CityID", "HO_DistrictID", "HO_WardID", "HO_AddressFullText",
        "MAIN_BUSINESS_CODE", "MAIN_BUSINESS_NAME",
    ]

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        offset, limit = 0, 1000
        backoff = 1.0

        while True:
            try:
                data = fetch_page(offset=offset, limit=limit)
            except requests.HTTPError as e:
                # Retry/backoff đơn giản
                if e.response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(backoff); backoff = min(backoff * 2, 30)
                    continue
                raise

            # Tuỳ cấu trúc trả về: ví dụ { "data": [ ... ], "total": N } hoặc { "items": [...], "hasMore": bool }
            items = data.get("data") or data.get("items") or []
            if not items:
                break

            for it in items:
                # it là bản ghi "EntInfo" rút gọn ở danh sách; có thể gọi detail để lấy đủ ngành nghề/đại diện
                ent_code = it.get("ENTERPRISE_CODE") or it.get("enterpriseCode")
                details = {}
                try:
                    details = fetch_detail(ent_code) if ent_code else {}
                except Exception:
                    details = {}

                ent = details.get("EntInfo") or details or it

                # Đọc các trường theo tài liệu 3558 (EntInfo, Representatives, HOAdress, BusinessActivity)
                reps = ent.get("Representatives") or {}
                ho   = ent.get("HOAdress") or {}
                biz  = ent.get("BusinessActivity") or {}

                row = {
                    "ENTERPRISE_CODE":       ent.get("ENTERPRISE_CODE") or ent_code,
                    "ENTERPRISE_GDT_CODE":   ent.get("ENTERPRISE_GDT_CODE"),
                    "NAME":                  ent.get("NAME"),
                    "ENTERPRISE_TYPE_NAME":  ent.get("ENTERPRISE_TYPE_NAME"),
                    "ENTERPRISE_STATUS_NAME":ent.get("ENTERPRISE_STATUS_NAME"),
                    "FOUNDING_DATE":         ent.get("FOUNDING_DATE"),
                    "LAST_AMEND_DATE":       ent.get("LAST_AMEND_DATE"),
                    "REPRESENTATIVE_FULL_NAME": reps.get("FULL_NAME"),
                    "HO_CityID":             ho.get("CityID"),
                    "HO_DistrictID":         ho.get("DistrictID"),
                    "HO_WardID":             ho.get("WardID"),
                    "HO_AddressFullText":    ho.get("AddressFullText"),
                    "MAIN_BUSINESS_CODE":    (biz.get("Code") if isinstance(biz, dict) else None),
                    "MAIN_BUSINESS_NAME":    (biz.get("Name") if isinstance(biz, dict) else None),
                }
                writer.writerow(row)
                total += 1

            # Cập nhật phân trang
            if "hasMore" in data:
                if not data["hasMore"]:
                    break
                offset += limit
            elif "total" in data:
                offset += limit
                if offset >= int(data["total"]):
                    break
            else:
                # nếu server trả về nextToken
                next_token = data.get("nextToken")
                if not next_token:
                    break
                # ví dụ đổi sang pageToken
                global LIST_ENDPOINT
                LIST_ENDPOINT = f"{BASE_URL}/enterprises/search?{urlencode({'pageToken': next_token})}"

        print(f"Đã ghi {total} dòng vào {out_file}")

if __name__ == "__main__":
    main()
