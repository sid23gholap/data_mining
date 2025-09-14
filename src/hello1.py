from bs4 import BeautifulSoup

html = """
 <tr class="comparison_table_image_row">
                <td class="comparison_table_first_col"></td>

                <th class="comparison_image_title_cell" role="columnheader">
                    <div class="a-row a-spacing-top-micro">
                        <center>
                             <img alt="Leviton 5207 125/250V Flush Mount Receptacle" src="https://images-na.ssl-images-amazon.com/images/I/31zkiMpPMBL._SL500_AC_SS350_.jpg" id="comparison_image">
                        </center>
                    </div>
                    <div class="a-row a-spacing-top-small">
                        <div id="comparison_title" class="a-section a-spacing-none">
                            <span aria-hidden="true" class="a-size-base a-color-base a-text-bold">
                                This item
                            </span>
                            <span aria-hidden="true" class="a-size-base a-color-base">Leviton 5207 125/250V Flush Mount Receptacle</span>
                        </div>
                    </div>
                </th>

                    <th class="comparison_image_title_cell comparable_item0" role="columnheader">
                        <a class="a-link-normal" target="_self" rel="noopener" href="/dp/B000FPDO4Y/ref=psdc_13397451_t1_B00002NARC">
                          <div class="a-row a-spacing-top-micro">
                            <center>
                                <img alt="" src="https://images-na.ssl-images-amazon.com/images/I/41Dtpf%2BbZTL._SL500_AC_SS350_.jpg" aria-hidden="true" id="comparison_image0">
                            </center>
                          </div>
                          <div id="comparison_title0" class="a-row a-spacing-top-small">
                            <span class="a-size-base">EATON WD125 3-Pole 3-Wire 30-Amp 125-Volt Surface Mount Dryer Power Receptacle, Black</span>
                          </div>
                        </a>
                    </th>
                
                    <th class="comparison_image_title_cell comparable_item1" role="columnheader">
                        <a class="a-link-normal" target="_self" rel="noopener" href="/dp/B00IPUA5ZW/ref=psdc_13397451_t2_B00002NARC">
                          <div class="a-row a-spacing-top-micro">
                            <center>
                                <img alt="" src="https://images-na.ssl-images-amazon.com/images/I/41Cxm39wsTL._SL500_AC_SS350_.jpg" aria-hidden="true" id="comparison_image1">
                            </center>
                          </div>
                          <div id="comparison_title1" class="a-row a-spacing-top-small">
                            <span class="a-size-base">General Electric WX09X10004 3 Wire 30amp Dryer Cord, 6-Feet</span>
                          </div>
                        </a>
                    </th>
                
                    <th class="comparison_image_title_cell comparable_item2" role="columnheader">
                        <a class="a-link-normal" target="_self" rel="noopener" href="/dp/B008KMTRLS/ref=psdc_13397451_t3_B00002NARC">
                          <div class="a-row a-spacing-top-micro">
                            <center>
                                <img alt="" src="https://images-na.ssl-images-amazon.com/images/I/51Zt1xKauOL._SL500_AC_SS350_.jpg" aria-hidden="true" id="comparison_image2">
                            </center>
                          </div>
                          <div id="comparison_title2" class="a-row a-spacing-top-small">
                            <span class="a-size-base">Bryant Electric RR330F, Outlet, Range Receptacle, Black</span>
                          </div>
                        </a>
                    </th>
                
                    <th class="comparison_image_title_cell comparable_item3" role="columnheader">
                        <a class="a-link-normal" target="_self" rel="noopener" href="/dp/B00004YUMW/ref=psdc_13397451_t4_B00002NARC">
"""

soup = BeautifulSoup(html, "html.parser")

asins = []
for a in soup.find_all("a", href=True):
    if "/dp/" in a["href"]:
        asin = a["href"].split("/dp/")[1].split("/")[0]
        asins.append(asin)

print(asins)
