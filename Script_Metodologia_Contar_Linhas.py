# -*- coding: utf-8 -*-

# Definir o caminho do ambiente de trabalho em que se encontra os shapefiles
arcpy.env.workspace = r"E:\Pessoal\UNB\2_2019\Metodologia"

# Definir variaveis
Distancia_Buffer_Metro = 1000
Distancia_Buffer_Linhas_Diretas_Onibus_UnB = 450
Distancia_Buffer_Linhas_Onibus_Rodoviaria = 450
Nome_Buffer_Linhas_Diretas_Onibus_UnB = "Buffer_Linhas_Diretas_Onibus_UnB_" + str(Distancia_Buffer_Linhas_Diretas_Onibus_UnB) + "M"
Nome_Buffer_Metro = "Buffer_Metro_" + str(Distancia_Buffer_Metro) + "M"
Nome_Buffer_Linhas_Onibus_Rodoviaria = "Buffer_Linhas_Onibus_Rodoviaria_" + str(Distancia_Buffer_Linhas_Onibus_Rodoviaria) + "M"

# 1. Producao da area de cobertura de linhas diretas para o campus Darcy Ribeiro

# 1.1. Producao da area de cobertura de linhas diretas de onibus para a UnB

# 1.1.1. Selecionar linhas diretas de onibus para a UnB
arcpy.SelectLayerByLocation_management(in_layer="vew_linhas ativas", overlap_type="INTERSECT",
                                      select_features="Selecao_linhas_de_onibus_diretas_UnB", selection_type="NEW_SELECTION")

# 1.1.2. Realizar o Buffer nas linhas diretas de onibus para a UnB agrupando as feicoes em relacao ao campo "linha"
arcpy.Buffer_analysis(in_features="vew_linhas ativas", out_feature_class="Buffer_Linhas_Diretas_Onibus_UnB_" + str(Distancia_Buffer_Linhas_Diretas_Onibus_UnB) + "M",
                     buffer_distance_or_field=str(Distancia_Buffer_Linhas_Diretas_Onibus_UnB) + " Meters",
                     dissolve_option="LIST", dissolve_field="linha")

# 1.2. Producao da area de cobertura de linhas integradas para a Rodoviaria do Plano Piloto

# 1.2.1. Producao da area de cobertura das estacoes de metro para a Rodoviaria do Plano Piloto

# 1.2.1.2. Selecionar as estacoes em operacao
arcpy.SelectLayerByAttribute_management(in_layer_or_view="Estação de Metrô", selection_type="NEW_SELECTION", where_clause='"situacao" = \'Em operação\'')

# 1.2.1.3. Realizar o Buffer nas estacoes em operacao agrupando as feicoes em relacao ao campo "linha"
arcpy.Buffer_analysis(in_features="Estação de Metrô", out_feature_class="Buffer_Metro_" + str(Distancia_Buffer_Metro) + "M",
                     buffer_distance_or_field=str(Distancia_Buffer_Metro) +  " Meters", 
                     dissolve_option="LIST", dissolve_field="linha")

# 1.2.2. Producao de area de cobertura das Linhas de Onibus Rodoviaria

# 1.2.2.1. Selecionar linhas de onibus proximas da Rodoviaria
arcpy.SelectLayerByLocation_management(in_layer="vew_linhas ativas", overlap_type="INTERSECT",
                                      select_features="Selecao_Linhas_de_Onibus_Rodoviaria", selection_type="NEW_SELECTION")

# 1.2.2.2. Realizar o Buffer nas linhas de onibus para a Rodoviaria agrupando as feicoes em relacao ao campo "linha"
arcpy.Buffer_analysis(in_features="vew_linhas ativas", out_feature_class="Buffer_Linhas_Onibus_Rodoviaria_" + str(Distancia_Buffer_Linhas_Onibus_Rodoviaria) + "M",
                     buffer_distance_or_field=str(Distancia_Buffer_Linhas_Onibus_Rodoviaria) + " Meters",
                     dissolve_option="LIST", dissolve_field="linha")

# 1.2.3. Unir o Buffer do metro e o Buffer das linhas de onibus para Rodoviaria

arcpy.Merge_management(inputs= '"' + Nome_Buffer_Metro + ";" + Nome_Buffer_Linhas_Onibus_Rodoviaria + '"',
                      output="Buffer_STP_Metro_Linhas_Onibus_Rodoviaria",
                      field_mappings='linha "linha" true true false 50 Text 0 0 ,First,#,' + Nome_Buffer_Metro + ',linha,-1,-1,' + Nome_Buffer_Linhas_Onibus_Rodoviaria + ',linha,-1,-1')

# 2. Producao das areas urbanas cobertas por Regiao Administrativa (RA)

# 2.2. Definir as areas urbanas das RAs fazendo a interseccao entre as feicoes das RAs e da area urbana do estudo da Embrapa
arcpy.Intersect_analysis(in_features="areas_urbanas_br_15 #;Macrozonas_Corrigidas #",
                        out_feature_class="Area_Urbana_RAs",
                       join_attributes="ALL", output_type="INPUT")

# 2.2. Dissolver o shapefile para que cada RAs possua apenas uma feicao
arcpy.Dissolve_management(in_features="Area_Urbana_RAs",
                         out_feature_class="Area_Urbana_RAs_Corrigida",
                        dissolve_field="RA_NOME", statistics_fields="", multi_part="MULTI_PART")

# 3. Realizar as comparacoes de area urbana e area de cobertura do Transporte Publico

# 3.1. Comparar o Buffer da area urbana corrigida e o Buffer das linhas diretas de onibus para UnB
arcpy.TabulateIntersection_analysis(in_zone_features="Area_Urbana_RAs_Corrigida", zone_fields="RA_NOME",
                                   in_class_features= Nome_Buffer_Linhas_Diretas_Onibus_UnB,
                                  out_table="P_Area_Urbana_Coberta_pelo_STP_Linhas_Diretas_Onibus_UnB.dbf",
                                 class_fields="linha", sum_fields="", xy_tolerance="-1 Unknown", out_units="UNKNOWN")

# 3.2. Exportar a tabela P_Area_Urbana_Coberta_pelo_STP_Linhas_Diretas_Onibus_UnB.dbf em formato .xls
arcpy.TableToExcel_conversion(Input_Table="P_Area_Urbana_Coberta_pelo_STP_Linhas_Diretas_Onibus_UnB.dbf",
                             Output_Excel_File="P_Area_Urbana_Coberta_pelo_STP_Linhas_Diretas_Onibus_UnB.xls",
                            Use_field_alias_as_column_header="NAME", Use_domain_and_subtype_description="CODE")

# 3. Realizar as comparacoes de area urbana e influencia do Transporte Publico

# 3.1. Comparar o Buffer da area urbana corrigida e o Buffer da uniao do metro e das linhas de onibus para Rodoviaria
arcpy.TabulateIntersection_analysis(in_zone_features="Area_Urbana_RAs_Corrigida", zone_fields="RA_NOME",
                                   in_class_features="Buffer_STP_Metro_Linhas_Onibus_Rodoviaria",
                                  out_table="P_Area_Urbana_Coberta_pelo_STP_Metro_Linhas_Onibus_Rodoviaria.dbf",
                                 class_fields="linha", sum_fields="", xy_tolerance="-1 Unknown", out_units="UNKNOWN")

# 3.2. Exportar a tabela P_Area_Urbana_Coberta_pelo_STP_Metro_Linhas_Onibus_Rodoviaria.dbf em formato .xls
arcpy.TableToExcel_conversion(Input_Table="P_Area_Urbana_Coberta_pelo_STP_Metro_Linhas_Onibus_Rodoviaria.dbf",
                             Output_Excel_File="P_Area_Urbana_Coberta_pelo_STP_Metro_Linhas_Onibus_Rodoviaria.xls",
                            Use_field_alias_as_column_header="NAME", Use_domain_and_subtype_description="CODE")
