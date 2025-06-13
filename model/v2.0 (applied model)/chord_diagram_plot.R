library(circlize)
library(readxl)

# Set working directory to script location
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)
setwd(script_dir)

# Country Abbreviations
country_abbreviations <- list(
  "Qatar" = "QA", "Australia" = "AU", "USA" = "US", "Russia" = "RU", "Malaysia" = "MY",
  "Nigeria" = "NG", "Trinidad & Tobago" = "TT", "Algeria" = "DZ", "Indonesia" = "ID",
  "Oman" = "OM", "Other Asia Pacific" = "OAP", "Other Europe" = "OE", "Other Americas" = "OA",
  "Other ME" = "OME", "Other Africa" = "OAF", "Japan" = "JP", "China" = "CN",
  "South Korea" = "KR", "India" = "IN", "Taiwan" = "TW", "Pakistan" = "PK",
  "France" = "FR", "Spain" = "ES", "UK" = "GB", "Italy" = "IT", "Turkey" = "TR",
  "Belgium" = "BE", "Total North America" = "TNA", "Total S. & C. America" = "SCA",
  "Total ME & Africa" = "TMEA"
)

# Group European Importers into "Europe"
# european_countries <- c("FR", "ES", "GB", "IT", "TR", "BE")
# country_abbreviations <- lapply(country_abbreviations, function(x) if (x %in% european_countries) "EU+" else x)

# Define region colors
region_colors <- c(
  "QA" = "#7886C7", "AU" = "#B5A8D5", "US" = "#FFA725", "RU" = "#99CCFF",
  "MY" = "#48A6A7", "NG" = "#FF9999", "TT" = "#FFB6C1", "DZ" = "#FFF599",
  "ID" = "#CC99FF", "OM" = "#0118D8", "OAP" = "#CFCFCF", "OE" = "#CCFFCC",
  "OA" = "#C1CFA1", "OME" = "#D3CA79", "OAF" = "#D2665A", "JP" = "#CFCFCF",
  "CN" = "#CFCFCF", "KR" = "#CFCFCF", "IN" = "#CFCFCF", "TW" = "#CFCFCF",
  "PK" = "#CFCFCF", "ES" = "#004494", "TNA" = "#CFCFCF", "SCA" = "#CFCFCF",
  "TMEA" = "#CFCFCF", "FR" = '#004494', "GB" = '#004494', "IT" = '#004494', "BE" = '#004494',
  "TR" = "#CFCFCF"
)

################################################################################

folders <- list.dirs("result", full.names = TRUE, recursive = FALSE)


for (dict in folders) {
  
  years <- c(2030, 2040)
  
  for (year in years) {
    
    # Load data
    file_path <- paste0(dict, "/flowsx", year, ".xlsx")
    data <- read_excel(file_path)
    row_names <- data[[1]]
    data_matrix <- as.matrix(data[,-1])
    
    rownames(data_matrix) <- sapply(row_names, function(x) country_abbreviations[[x]])
    colnames(data_matrix) <- sapply(colnames(data)[-1], function(x) country_abbreviations[[x]])
    
    flow_matrix <- as.matrix(data_matrix)
    total_exports <- rowSums(flow_matrix)
    total_imports <- colSums(flow_matrix)
    
    write.csv(flow_matrix, 'test_flow_matrix.csv')
    
    # PDF output
    output_file <- paste0(dict, "/chord_diagram_", year, ".pdf")
    pdf(output_file, width = 9.5, height = 8.5)
    
    # Chord diagram
    chordDiagram(
      flow_matrix,
      grid.col = region_colors,
      transparency = 0.15,
      annotationTrack = c("grid"),
      preAllocateTracks = list(track.height = 0.125)
    )
    
    font_size <- 1.5
    label_offset <- 0.2
    
    # Add text labels and background boxes
    circos.track(track.index = 1, panel.fun = function(x, y) {
      sector.name <- get.cell.meta.data("sector.index")
      sector.xlim <- get.cell.meta.data("xlim")
      sector.ylim <- get.cell.meta.data("ylim")
      
      if (!is.numeric(sector.xlim) || !is.numeric(sector.ylim)) return()
      
      # Flow data
      total_flow <- ifelse(sector.name %in% names(total_exports), total_exports[sector.name],
                           ifelse(sector.name %in% names(total_imports), total_imports[sector.name], NA))
      
      # Sector label
      
      
      # Flow value label
      if (!is.na(total_flow) && total_flow > 1) {
        
        if (total_flow > 15){
          circos.text(
            x = mean(sector.xlim),
            y = max(sector.ylim) + 2.25 * label_offset,
            labels = paste0("(", round(total_flow, 0), ")"),
            facing = "bending.inside",
            niceFacing = TRUE,
            cex = font_size
          )
        }
        
        circos.rect(
          xleft = sector.xlim[1],
          ybottom = sector.ylim[1],
          xright = sector.xlim[2],
          ytop = sector.ylim[2],
          col = region_colors[sector.name],
          border = NA
        )
        
        circos.text(
          x = mean(sector.xlim),
          y = max(sector.ylim) - 0.5,
          labels = sector.name,
          facing = "clockwise",
          niceFacing = TRUE,
          cex = font_size,
        )
        
      } else {
        # Background color box for empty flows
        circos.rect(
          xleft = sector.xlim[1],
          ybottom = sector.ylim[1],
          xright = sector.xlim[2],
          ytop = sector.ylim[2],
          col = "#CFCFCF",
          border = NA
        )
        
        circos.text(
          x = mean(sector.xlim),
          y = max(sector.ylim) - 0.5,
          labels = sector.name,
          facing = "clockwise",
          niceFacing = TRUE,
          cex = font_size,
          col='black'
        )
      }
    })
    
    dev.off()
    circos.clear()
  }
}


