import arcpy

# initialisation de l'environnement de travail
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\nsama\Documents\ArcGIS\Projects\data"
arcpy.management.CreateFileGDB("base_de_donnee", "db_regions")

# impportation des données
region = r"C:\Users\nsama\Documents\ArcGIS\Projects\data\REGION.shp"
departement = r"C:\Users\nsama\Documents\ArcGIS\Projects\data\DEPARTEMENT.shp"
rivers = r"C:\Users\nsama\Documents\ArcGIS\Projects\data\riviere.shp"
roads = r"C:\Users\nsama\Documents\ArcGIS\Projects\data\route.shp"

# création de couche temporaires
region_feature = arcpy.management.MakeFeatureLayer(region)
departement_feature = arcpy.management.MakeFeatureLayer(departement)
rivers_feature = arcpy.management.MakeFeatureLayer(rivers)
roads_feature = arcpy.management.MakeFeatureLayer(roads)

# chemin vers la base de données
root_bdd = r"C:\Users\nsama\Documents\ArcGIS\Projects\data\base_de_donnee\db_region.gdb"
fields = ["NOM_REG"]

liste_of_region = []
with arcpy.da.SearchCursor(region, fields) as cursor:
    for row in cursor :
        liste_of_region.append(row[0])

region_feature = arcpy.MakeFeatureLayer_management(region)
departement_feature = arcpy.MakeFeatureLayer_management(departement)
rivers_feature = arcpy.MakeFeatureLayer_management(rivers)
roads_feature = arcpy.MakeFeatureLayer_management(roads)

fields = ["NOM_REG"]
bdd = r"base_de_donnee\db_regions.gdb"
liste_of_shp = [region_feature, departement_feature, rivers_feature, roads_feature]



# récupération de la liste des régions afin de les sauvegarder si l'argument All est passé à la fonction
liste_of_region = []
with arcpy.da.SearchCursor(region, fields) as cursor:
    for row in cursor:
        liste_of_region.append(row[0])
del cursor

"""
@param: liste of shp
return : stock les shp dans une base de données 
"""
def sotre_list_of_shp(shp_liste, base_de_donnee):
    for shp in shp_liste:
        arcpy.FeatureClassToGeodatabase_conversion(shp, base_de_donnee)

"""
@:param: chaine de caractère. nom d'une région ou All
return : geodatabase avec les couches rivière, routes, departement et region
"""
def create_gdb_region(entree):
    with arcpy.da.SearchCursor(region, fields) as cursor:
        for row in cursor:
            if entree == row[0]:
                # selection de la région par attribut en fonction de l'éntrée de l'utilisateur
                where_clause = "NOM_REG = '{0}'".format(entree)
                region_selected = arcpy.SelectLayerByAttribute_management(region_feature, "NEW SELECTION", where_clause)
                # creation de la couche temporaire à sauvegarder dans la gdb
                region_selected_feature = arcpy.MakeFeatureLayer_management(region_selected, "Region_{}".format(entree))
                # sauvegarde de la couche dans la géodatabase
                arcpy.FeatureClassToGeodatabase_conversion(region_selected_feature, r"base_de_donnee\db_regions.gdb")
                # selection des department inclus dans la region
                departement_selected = arcpy.SelectLayerByLocation_management(departement_feature, "WITHIN",
                                                                              region_selected_feature)
                department_selected_feature = arcpy.MakeFeatureLayer_management(departement_selected,
                                                                                "Departement_{}".format(entree))
                # sauvegarde de la couche departmenet dans la geodatabase
                arcpy.FeatureClassToGeodatabase_conversion(department_selected_feature,
                                                           r"base_de_donnee\db_regions.gdb")

                # selection des routes incluses dans la region selectionnée par l'utilisateur
                roads_selected = arcpy.analysis.Clip(roads_feature, region_feature,
                                                     r"base_de_donnee\db_regions.gdb\routes_selection", None)
                roads_selected_feature = arcpy.MakeFeatureLayer_management(roads_selected, "Routes{}".format(entree))
                arcpy.FeatureClassToGeodatabase_conversion(roads_selected_feature, r"base_de_donnee\db_regions.gdb")

                # selection des rivières incluses dans la région selectionnée par l'utilisateur
                rivers_selected = arcpy.analysis.Clip(rivers_feature, region_feature,
                                                      r"base_de_donnee\db_regions.gdb\routes_selection", None)
                rivers_selected_feature = arcpy.MakeFeatureLayer_management(rivers_selected,
                                                                            "Rivieres{}".format(entree))
                arcpy.FeatureClassToGeodatabase_conversion(rivers_selected_feature, r"base_de_donnee\db_regions.gdb")

            elif entree.lower() != 'all' and entree not in liste_of_region:
                print(f"veuillez un nom de région valide parmi ceux présent dans cette liste : {liste_of_region} OU ALL pour exporter tout.")
                break
        if entree.lower() == 'all':
            sotre_list_of_shp(liste_of_shp, bdd)
        else:
            pass

if __name__ == "__main__":

    create_gdb_region("Occitanie")


