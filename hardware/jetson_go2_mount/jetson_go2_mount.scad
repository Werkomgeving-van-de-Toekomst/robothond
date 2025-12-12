/*
 * Jetson AGX Orin Mount voor Unitree Go2 Robot
 * 
 * Dit ontwerp is gebaseerd op:
 * - Unitree Go2 Payload specificaties: https://support.unitree.com/home/en/developer/Payload
 * - Jetson AGX Orin Developer Kit afmetingen
 * 
 * MONTAGE METHODE:
 * - Deze mount gebruikt T-slot rails die in de Go2 payload gleuven schuiven
 * - Schuif de rails aan beide kanten in de Go2 gleuven
 * - Geen schroeven nodig - de T-slot vorm houdt de mount op zijn plek
 * - Zet use_slide_rails = true voor gleuf montage
 * - Zet use_slide_rails = false en use_mount_tabs = true voor schroef montage
 * 
 * Auteur: Go2 Robot Project
 * Licentie: MIT
 * 
 * Print instellingen:
 * - Materiaal: PETG of ABS (sterker dan PLA)
 * - Layer hoogte: 0.2mm
 * - Infill: 40-50%
 * - Supports: Ja (voor rails)
 * - Print orientatie: Plat op bed, rails naar beneden
 */

// === PARAMETERS ===

// Jetson AGX Orin afmetingen (mm)
jetson_width = 110;
jetson_depth = 110;
jetson_height = 71.65;

// Jetson mounting holes (M3, 4 hoeken)
jetson_hole_diameter = 3.2;
jetson_hole_inset = 4;  // Afstand van rand tot hole center

// Go2 payload rail afmetingen (gebaseerd op Unitree Payload specs)
go2_rail_width = 150;       // Breedte tussen rails
go2_rail_depth = 200;       // Lengte van payload area
go2_mount_hole_diameter = 5; // M4 of M5 mounting holes
go2_mount_hole_spacing_x = 140;
go2_mount_hole_spacing_y = 180;

// Go2 payload rail gleuf specificaties (T-slot rails)
go2_groove_width = 6;       // Breedte van de gleuf (mm)
go2_groove_depth = 3;       // Diepte van de gleuf (mm)
go2_groove_spacing = 150;   // Afstand tussen gleuven (center to center)
go2_rail_length = 180;      // Lengte van de rail (moet in gleuf passen)
go2_rail_thickness = 2.5;   // Dikte van de rail (iets kleiner dan gleuf voor speling)
go2_rail_height = 6;        // Totale hoogte van de rail (steel + T-top, moet in gleuf passen)

// Mount plaat parameters
// Plate breedte moet overeenkomen met Go2 gleuf spacing voor juiste uitlijning
plate_thickness = 4;
plate_width = go2_groove_spacing;  // Gelijk aan gleuf spacing voor perfecte uitlijning
plate_depth = 140;
plate_corner_radius = 8;

// Bereken totale breedte met converter
total_width = include_converter_mount ? 
    plate_width + converter_mount_spacing + converter_width + 4 : 
    plate_width;

// Jetson standoff parameters
standoff_height = 15;       // Ruimte voor ventilatie
standoff_diameter = 8;
standoff_hole_diameter = 3.2;

// Ventilatie gaten
vent_hole_diameter = 10;
vent_hole_spacing = 15;

// Kabel doorvoer
cable_slot_width = 25;
cable_slot_depth = 15;

// Powerbank houder (optioneel)
include_powerbank_mount = false;
powerbank_width = 80;
powerbank_depth = 160;
powerbank_height = 30;

// DC-DC Converter mount (voor Go2 power outlet)
include_converter_mount = true;
converter_width = 101;      // Mean Well SD-100A-12
converter_depth = 51;
converter_height = 30;
converter_mount_spacing = 15;  // Afstand tussen Jetson en converter

// Lip/rand voor extra stevigheid
lip_height = 8;
lip_thickness = 2;

// Mounting opties
use_slide_rails = true;      // Gebruik T-slot rails (schuiven in gleuven)
use_mount_tabs = false;      // Gebruik mounting tabs (schroeven) - alleen als use_slide_rails = false

// === MODULES ===

// Afgeronde rechthoek
module rounded_rect(width, depth, height, radius) {
    hull() {
        for (x = [radius, width - radius]) {
            for (y = [radius, depth - radius]) {
                translate([x, y, 0])
                    cylinder(h = height, r = radius, $fn = 32);
            }
        }
    }
}

// Ventilatie patroon
module ventilation_pattern(width, depth, hole_d, spacing) {
    cols = floor((width - hole_d) / spacing);
    rows = floor((depth - hole_d) / spacing);
    
    start_x = (width - (cols - 1) * spacing) / 2;
    start_y = (depth - (rows - 1) * spacing) / 2;
    
    for (x = [0 : cols - 1]) {
        for (y = [0 : rows - 1]) {
            translate([start_x + x * spacing, start_y + y * spacing, -1])
                cylinder(h = plate_thickness + 2, d = hole_d, $fn = 24);
        }
    }
}

// Standoff voor Jetson mounting
module standoff(height, outer_d, hole_d) {
    difference() {
        cylinder(h = height, d = outer_d, $fn = 32);
        translate([0, 0, -1])
            cylinder(h = height + 2, d = hole_d, $fn = 24);
    }
}

// Go2 T-slot rail (schuift in Go2 payload gleuven)
// Deze module maakt een duidelijke T-vorm die in de Go2 gleuven schuift
module go2_t_slot_rail(length, groove_width, groove_depth, rail_thickness, rail_height) {
    // T-slot afmetingen met speling voor soepel schuiven
    // De steel moet smaller zijn dan de gleuf opening om erdoor te kunnen
    // De T-top moet breder zijn dan de steel om achter de gleuf te blijven
    
    // Steel afmetingen (onderste deel dat door de gleuf opening past)
    steel_width = groove_width - 0.8;        // Steel (0.8mm smaller dan gleuf voor speling)
    steel_height = groove_depth - 0.2;       // Hoogte steel (iets kleiner dan gleuf diepte)
    
    // T-top afmetingen (bovenste deel dat achter de gleuf blijft)
    t_top_width = groove_width + 4.0;        // T-top (4mm breder dan gleuf - duidelijk zichtbaar!)
    t_top_height = rail_height - steel_height; // Rest van de hoogte voor T-top
    
    // Start vanaf de onderkant (negatieve Z voor onder de plate)
    translate([0, 0, -rail_height]) {
        // Steel (onderste deel, past door gleuf opening)
        // Centreer steel binnen de groef breedte
        steel_x_offset = (groove_width - steel_width) / 2;
        translate([steel_x_offset, 0, 0]) {
            cube([steel_width, length, steel_height]);
        }
        
        // T-top (bovenste deel, blijft achter gleuf - duidelijk zichtbaar als T-vorm)
        // T-top is breder dan steel, waardoor duidelijke T-vorm ontstaat
        t_top_x_offset = (groove_width - t_top_width) / 2;
        translate([t_top_x_offset, 0, steel_height]) {
            cube([t_top_width, length, t_top_height]);
        }
    }
}

// Go2 mounting tab (voor schroef bevestiging, optioneel)
module go2_mount_tab(hole_d) {
    tab_width = 20;
    tab_depth = 15;
    
    difference() {
        // Tab body
        hull() {
            translate([0, 0, 0])
                cylinder(h = plate_thickness, d = tab_width, $fn = 32);
            translate([0, -tab_depth/2, 0])
                cube([tab_width/2, tab_depth, plate_thickness]);
        }
        
        // Mounting hole
        translate([0, 0, -1])
            cylinder(h = plate_thickness + 2, d = hole_d, $fn = 24);
    }
}

// Kabel doorvoer slot
module cable_slot(width, depth) {
    hull() {
        translate([0, 0, -1])
            cylinder(h = plate_thickness + 2, d = depth, $fn = 24);
        translate([width - depth, 0, -1])
            cylinder(h = plate_thickness + 2, d = depth, $fn = 24);
    }
}

// Jetson retaining lip
module jetson_lip(width, depth, height, thickness) {
    // Achter lip
    translate([0, 0, plate_thickness])
        cube([width, thickness, height]);
    
    // Linker lip
    translate([0, 0, plate_thickness])
        cube([thickness, depth, height]);
    
    // Rechter lip
    translate([width - thickness, 0, plate_thickness])
        cube([thickness, depth, height]);
    
    // Voor lip (met opening voor kabels)
    translate([0, depth - thickness, plate_thickness])
        difference() {
            cube([width, thickness, height]);
            // Kabel opening
            translate([width/2 - cable_slot_width/2, -1, -1])
                cube([cable_slot_width, thickness + 2, height + 2]);
        }
}

// Powerbank houder
module powerbank_mount(width, depth, height) {
    wall = 3;
    
    translate([plate_width + 10, (plate_depth - depth) / 2, 0]) {
        difference() {
            // Outer shell
            cube([width + wall * 2, depth + wall * 2, height + plate_thickness]);
            
            // Inner cutout
            translate([wall, wall, plate_thickness])
                cube([width, depth, height + 1]);
            
            // Strap slots
            for (y = [20, depth - 10]) {
                translate([-1, wall + y, plate_thickness + height/2])
                    rotate([0, 90, 0])
                        cylinder(h = width + wall * 2 + 2, d = 5, $fn = 24);
            }
        }
    }
}

// DC-DC Converter mount (voor Go2 power outlet)
module converter_mount(width, depth, height) {
    wall = 2;
    standoff_height = 5;
    standoff_diameter = 6;
    hole_diameter = 3.2;
    
    // Converter wordt 90 graden gedraaid: width en depth wisselen om
    // Na rotatie: originele depth wordt nieuwe breedte, originele width wordt nieuwe diepte
    rotated_width = depth;   // Na rotatie wordt dit de nieuwe breedte (X-richting)
    rotated_depth = width;   // Na rotatie wordt dit de nieuwe diepte (Y-richting)
    
    // Converter mounting plate (naast Jetson, in verlengde van basisplaat)
    // Na 90 graden rotatie: converter plaat heeft rotated_width als breedte
    converter_plate_width = rotated_width + wall * 2;
    converter_plate_depth = rotated_depth + wall * 2;
    
    // Positie: converter_x blijft hetzelfde, converter_y moet gecentreerd worden op basisplaat
    converter_x = plate_width + converter_mount_spacing;
    converter_y = (plate_depth - converter_plate_depth) / 2;
    
    translate([converter_x, converter_y, 0]) {
        // Rotatie: 90 graden om Z-as (kwart slag), roteer om het midden van de plaat
        translate([converter_plate_width/2, converter_plate_depth/2, 0]) {
            rotate([0, 0, 90]) {
                translate([-converter_plate_depth/2, -converter_plate_width/2, 0]) {
                    // Basis plaat (na rotatie: width en depth zijn omgewisseld)
                    difference() {
                        cube([converter_plate_depth, converter_plate_width, plate_thickness]);
                        
                        // Ventilatie gaten (aanpassen voor geroteerde positie)
                        vent_spacing = 15;
                        for (x = [wall + 10 : vent_spacing : rotated_depth + wall - 10]) {
                            for (y = [wall + 10 : vent_spacing : rotated_width + wall - 10]) {
                                translate([x, y, -1])
                                    cylinder(h = plate_thickness + 2, d = 5, $fn = 16);
                            }
                        }
                    }
                    
                    // Standoffs voor converter mounting (Mean Well heeft 4 mounting holes)
                    // Na rotatie: hole_spacing_x en hole_spacing_y zijn omgewisseld
                    hole_spacing_x = rotated_depth - 20;
                    hole_spacing_y = rotated_width - 20;
                    
                    for (x_offset = [10, hole_spacing_x]) {
                        for (y_offset = [10, hole_spacing_y]) {
                            translate([wall + x_offset, wall + y_offset, plate_thickness]) {
                                difference() {
                                    cylinder(h = standoff_height, d = standoff_diameter, $fn = 24);
                                    translate([0, 0, -1])
                                        cylinder(h = standoff_height + 2, d = hole_diameter, $fn = 16);
                                }
                            }
                        }
                    }
                    
                    // Retaining walls (laag, voor stabiliteit) - na rotatie
                    translate([0, 0, plate_thickness])
                        cube([converter_plate_depth, wall, 5]);
                    translate([0, converter_plate_width - wall, plate_thickness])
                        cube([converter_plate_depth, wall, 5]);
                }
            }
        }
    }
    
    // Kabel doorvoer voor power kabels
    translate([plate_width, plate_depth/2 - 10, 0])
        cube([converter_mount_spacing, 20, plate_thickness + 5]);
}

// === MAIN ASSEMBLY ===

module jetson_go2_mount() {
    difference() {
        union() {
            // Basis plaat
            rounded_rect(plate_width, plate_depth, plate_thickness, plate_corner_radius);
            
            // Jetson standoffs
            jetson_offset_x = (plate_width - jetson_width) / 2;
            jetson_offset_y = (plate_depth - jetson_depth) / 2;
            
            for (x = [jetson_hole_inset, jetson_width - jetson_hole_inset]) {
                for (y = [jetson_hole_inset, jetson_depth - jetson_hole_inset]) {
                    translate([jetson_offset_x + x, jetson_offset_y + y, plate_thickness])
                        standoff(standoff_height, standoff_diameter, standoff_hole_diameter);
                }
            }
            
            // Retaining lips
            translate([jetson_offset_x, jetson_offset_y, 0])
                jetson_lip(jetson_width, jetson_depth, lip_height, lip_thickness);
            
            // Go2 mounting: T-slot rails (schuiven in gleuven)
            // Rails alleen onder basisplaat (niet onder converter mount)
            if (use_slide_rails) {
                // Bereken rail positie (gecentreerd op plate)
                rail_offset_y = (plate_depth - go2_rail_length) / 2;
                
                // Linker rail (schuift in linker gleuf van Go2)
                // Rail loopt langs de linker zijkant van basisplaat
                translate([-go2_groove_width/2, rail_offset_y, 0]) {
                    rotate([0, 0, 0])  // Geen rotatie, rail loopt in Y-richting
                        go2_t_slot_rail(
                            go2_rail_length,
                            go2_groove_width,
                            go2_groove_depth,
                            go2_rail_thickness,
                            go2_rail_height
                        );
                }
                
                // Rechter rail (schuift in rechter gleuf van Go2)
                // Rail loopt langs de rechter zijkant van basisplaat (originele breedte)
                translate([plate_width - go2_groove_width/2, rail_offset_y, 0]) {
                    rotate([0, 0, 0])  // Geen rotatie, rail loopt in Y-richting
                        go2_t_slot_rail(
                            go2_rail_length,
                            go2_groove_width,
                            go2_groove_depth,
                            go2_rail_thickness,
                            go2_rail_height
                        );
                }
            }
            
            // Go2 mounting tabs (optioneel, alleen als use_slide_rails = false)
            if (use_mount_tabs && !use_slide_rails) {
                // Voorste tabs
                translate([plate_width/2 - go2_mount_hole_spacing_x/2, -10, 0])
                    go2_mount_tab(go2_mount_hole_diameter);
                translate([plate_width/2 + go2_mount_hole_spacing_x/2, -10, 0])
                    go2_mount_tab(go2_mount_hole_diameter);
                
                // Achterste tabs
                translate([plate_width/2 - go2_mount_hole_spacing_x/2, plate_depth + 10, 0])
                    rotate([0, 0, 180])
                        go2_mount_tab(go2_mount_hole_diameter);
                translate([plate_width/2 + go2_mount_hole_spacing_x/2, plate_depth + 10, 0])
                    rotate([0, 0, 180])
                        go2_mount_tab(go2_mount_hole_diameter);
            }
            
            // Powerbank mount (optioneel)
            if (include_powerbank_mount) {
                powerbank_mount(powerbank_width, powerbank_depth, powerbank_height);
            }
            
            // DC-DC Converter mount (voor Go2 power outlet)
            if (include_converter_mount) {
                converter_mount(converter_width, converter_depth, converter_height);
            }
        }
        
        // Ventilatie gaten in het midden
        vent_area_width = jetson_width - 30;
        vent_area_depth = jetson_depth - 30;
        
        translate([(plate_width - vent_area_width) / 2, (plate_depth - vent_area_depth) / 2, 0])
            ventilation_pattern(vent_area_width, vent_area_depth, vent_hole_diameter, vent_hole_spacing);
        
        // Kabel doorvoer slots
        // Ethernet kabel slot (achter)
        translate([plate_width/2, plate_depth - 20, 0])
            cable_slot(cable_slot_width, cable_slot_depth);
        
        // Power kabel slot (zijkant)
        translate([plate_width - 20, plate_depth/2, 0])
            rotate([0, 0, 90])
                cable_slot(cable_slot_width, cable_slot_depth);
    }
}

// === RENDER ===

// Render de mount
jetson_go2_mount();

// Preview text (alleen zichtbaar in OpenSCAD)
// translate([plate_width/2, -25, 0])
//     linear_extrude(1)
//         text("Jetson AGX Orin Mount", size=8, halign="center");

