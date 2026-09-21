# import cadquery as cq
# import math


# # ==============================================================================
# # DEFAULT PARAMETERS
# # ==============================================================================

# stick_width = 9.10
# stick_thickness = 1.90
# clearance = 0.10

# pocket_thick = stick_thickness + clearance
# pocket_width = stick_width + clearance

# wall_thickness = 1.2
# base_thickness = 2.0
# overall_height = 13.6

# overall_outer_curve_height = 4.6
# overall_inner_curve_height = 4.0
# snap_lip_inward = 0.35

# tip_fillet_radius = 0.30
# pocket_fillet_radius = 0.30
# wall_arm_fillet_radius = 0.30
# tooth_fillet_radius = 0.15

# front_back_wall_height = 6.69

# # Teeth stop this distance short of both Z-side edges
# tooth_edge_margin = 0.50


# # ==============================================================================
# # ONE-WAY CONNECTOR
# # ==============================================================================

# def make_one_way_connector(
#     stick_width=stick_width,
#     stick_thickness=stick_thickness,
#     clearance=clearance,
#     wall_thickness=wall_thickness,
#     base_thickness=base_thickness,
#     overall_height=overall_height,
#     overall_outer_curve_height=overall_outer_curve_height,
#     overall_inner_curve_height=overall_inner_curve_height,
#     snap_lip_inward=snap_lip_inward,
#     tip_fillet_radius=tip_fillet_radius,
#     pocket_fillet_radius=pocket_fillet_radius,
#     wall_arm_fillet_radius=wall_arm_fillet_radius,
#     tooth_fillet_radius=tooth_fillet_radius,
#     front_back_wall_height=front_back_wall_height,
#     tooth_edge_margin=tooth_edge_margin,
# ):

#     # --------------------------------------------------------------------------
#     # Basic dimensions
#     # --------------------------------------------------------------------------

#     pocket_thick = stick_thickness + clearance
#     pocket_width = stick_width + clearance

#     clamp_depth = pocket_width + 2.0 * wall_thickness

#     gap_width = pocket_thick
#     half_gap = gap_width / 2.0
#     outer_x = half_gap + wall_thickness

#     straight_height = (
#         overall_height
#         - base_thickness
#         - overall_outer_curve_height
#     )

#     mid_y = base_thickness + straight_height

#     # --------------------------------------------------------------------------
#     # Outer arc
#     # --------------------------------------------------------------------------

#     R_o = (
#         overall_outer_curve_height**2
#         + snap_lip_inward**2
#     ) / (2.0 * snap_lip_inward)

#     x_c = outer_x - R_o
#     y_c = mid_y

#     sin_theta_outer = overall_outer_curve_height / R_o
#     theta_outer = math.asin(sin_theta_outer)

#     outer_tip_x = x_c + R_o * math.cos(theta_outer)
#     outer_tip_y = y_c + overall_outer_curve_height

#     # --------------------------------------------------------------------------
#     # Inner arc
#     # --------------------------------------------------------------------------

#     R_i = R_o - wall_thickness

#     if R_i <= 0:
#         raise ValueError(
#             "Wall thickness is too large for the calculated inner radius."
#         )

#     sin_theta_inner = overall_inner_curve_height / R_i

#     if not -1.0 <= sin_theta_inner <= 1.0:
#         raise ValueError(
#             "Inner curve height is too large for the calculated inner radius."
#         )

#     theta_inner = math.asin(sin_theta_inner)

#     inner_tip_x = x_c + R_i * math.cos(theta_inner)
#     inner_tip_y = y_c + overall_inner_curve_height

#     # --------------------------------------------------------------------------
#     # Arc midpoints
#     # --------------------------------------------------------------------------

#     outer_mid_x = x_c + R_o * math.cos(theta_outer / 2.0)
#     outer_mid_y = y_c + R_o * math.sin(theta_outer / 2.0)

#     inner_mid_x = x_c + R_i * math.cos(theta_inner / 2.0)
#     inner_mid_y = y_c + R_i * math.sin(theta_inner / 2.0)

#     # --------------------------------------------------------------------------
#     # Build one half
#     # --------------------------------------------------------------------------

#     half_clamp = (
#         cq.Workplane("XY")
#         .moveTo(0, 0)
#         .lineTo(outer_x, 0)
#         .lineTo(outer_x, mid_y)
#         .threePointArc(
#             (outer_mid_x, outer_mid_y),
#             (outer_tip_x, outer_tip_y)
#         )
#         .lineTo(inner_tip_x, inner_tip_y)
#         .threePointArc(
#             (inner_mid_x, inner_mid_y),
#             (half_gap, mid_y)
#         )
#         .lineTo(half_gap, base_thickness)
#         .lineTo(0, base_thickness)
#         .close()
#         .extrude(clamp_depth)
#     )

#     # --------------------------------------------------------------------------
#     # Tip fillets
#     # --------------------------------------------------------------------------

#     def tip_edge_selector(x, y):
#         eps = 0.05

#         return cq.selectors.BoxSelector(
#             (x - eps, y - eps, 0),
#             (x + eps, y + eps, clamp_depth)
#         )

#     half_clamp = half_clamp.edges(
#         tip_edge_selector(outer_tip_x, outer_tip_y)
#     ).fillet(tip_fillet_radius)

#     half_clamp = half_clamp.edges(
#         tip_edge_selector(inner_tip_x, inner_tip_y)
#     ).fillet(tip_fillet_radius)

#     # --------------------------------------------------------------------------
#     # Mirror left/right
#     # --------------------------------------------------------------------------

#     one_way_clamp = half_clamp.union(
#         half_clamp.mirror("YZ")
#     )

#     # --------------------------------------------------------------------------
#     # Front/back pocket walls
#     # --------------------------------------------------------------------------

#     pocket_center_y = (
#         base_thickness
#         + front_back_wall_height / 2.0
#     )

#     back_wall = (
#         cq.Workplane("XY")
#         .moveTo(0, pocket_center_y)
#         .rect(gap_width, front_back_wall_height)
#         .extrude(wall_thickness)
#     )

#     front_wall = (
#         cq.Workplane("XY")
#         .workplane(offset=clamp_depth - wall_thickness)
#         .moveTo(0, pocket_center_y)
#         .rect(gap_width, front_back_wall_height)
#         .extrude(wall_thickness)
#     )

#     pocket_walls = back_wall.union(front_wall)

#     one_way_clamp = one_way_clamp.union(pocket_walls)

#     # --------------------------------------------------------------------------
#     # Pocket fillets
#     # --------------------------------------------------------------------------

#     eps = 0.03

#     wall_y_bottom = base_thickness
#     wall_y_top = base_thickness + front_back_wall_height

#     for x_pos in (half_gap, -half_gap):

#         for z_pos in (
#             wall_thickness,
#             clamp_depth - wall_thickness
#         ):

#             selector = cq.selectors.BoxSelector(
#                 (
#                     x_pos - eps,
#                     wall_y_bottom - eps,
#                     z_pos - eps
#                 ),
#                 (
#                     x_pos + eps,
#                     wall_y_top + eps,
#                     z_pos + eps
#                 )
#             )

#             one_way_clamp = (
#                 one_way_clamp
#                 .edges(selector)
#                 .fillet(pocket_fillet_radius)
#             )

#     # --------------------------------------------------------------------------
#     # Side fillets where front/back cover meets straight arm
#     #
#     # These are the 4 restored cover/arm fillets.
#     # --------------------------------------------------------------------------

#     side_eps = 0.04

#     wall_top_y = (
#         base_thickness
#         + front_back_wall_height
#     )

#     for x_pos in (half_gap, -half_gap):

#         # Front cover / arm junction
#         front_selector = cq.selectors.BoxSelector(
#             (
#                 x_pos - side_eps,
#                 wall_top_y - side_eps,
#                 -side_eps
#             ),
#             (
#                 x_pos + side_eps,
#                 wall_top_y + side_eps,
#                 wall_thickness + side_eps
#             )
#         )

#         one_way_clamp = (
#             one_way_clamp
#             .edges(front_selector)
#             .fillet(wall_arm_fillet_radius)
#         )

#         # Back cover / arm junction
#         back_selector = cq.selectors.BoxSelector(
#             (
#                 x_pos - side_eps,
#                 wall_top_y - side_eps,
#                 clamp_depth - wall_thickness - side_eps
#             ),
#             (
#                 x_pos + side_eps,
#                 wall_top_y + side_eps,
#                 clamp_depth + side_eps
#             )
#         )

#         one_way_clamp = (
#             one_way_clamp
#             .edges(back_selector)
#             .fillet(wall_arm_fillet_radius)
#         )

#     # --------------------------------------------------------------------------
#     # Conformal internal friction teeth
#     #
#     # Teeth stop tooth_edge_margin short of both Z-side edges.
#     # --------------------------------------------------------------------------

#     def get_inner_x(y_val):
#         dy = y_val - y_c

#         return (
#             x_c
#             + math.sqrt(
#                 R_i**2 - dy**2
#             )
#         )

#     ridge_ys = [10.2, 11.2, 12.2]
#     prot = 0.20
#     tooth_half = 0.35

#     tooth_depth = (
#         clamp_depth
#         - 2.0 * tooth_edge_margin
#     )

#     if tooth_depth <= 0:
#         raise ValueError(
#             "tooth_edge_margin is too large."
#         )

#     # Keep track of tooth geometry so the exposed edges can be filleted
#     # AFTER the teeth are fused into the clamp.
#     for y_pos in ridge_ys:

#         y_bot = y_pos - tooth_half
#         y_top = y_pos + tooth_half

#         x_bot = get_inner_x(y_bot)
#         x_top = get_inner_x(y_top)
#         x_mid = get_inner_x(y_pos)

#         x_apex = x_mid - prot

#         right_tooth = (
#             cq.Workplane("XY")
#             .moveTo(
#                 x_bot + 0.05,
#                 y_bot
#             )
#             .lineTo(
#                 x_bot,
#                 y_bot
#             )
#             .threePointArc(
#                 (x_apex, y_pos),
#                 (x_top, y_top)
#             )
#             .lineTo(
#                 x_top + 0.05,
#                 y_top
#             )
#             .threePointArc(
#                 (x_mid + 0.05, y_pos),
#                 (x_bot + 0.05, y_bot)
#             )
#             .close()
#             .extrude(tooth_depth)
#             .translate(
#                 (
#                     0,
#                     0,
#                     tooth_edge_margin
#                 )
#             )
#         )

#         one_way_clamp = (
#             one_way_clamp
#             .union(right_tooth)
#             .union(right_tooth.mirror("YZ"))
#         )

#     # --------------------------------------------------------------------------
#     # Round the exposed front/back edges of the teeth
#     #
#     # 3 teeth × 2 sides × 2 Z faces = 12 edges
#     #
#     # This is intentionally done AFTER the tooth union.
#     # --------------------------------------------------------------------------

#     tooth_edges = []

#     for y_pos in ridge_ys:

#         x_mid = get_inner_x(y_pos)
#         x_apex = x_mid - prot

#         for x_sign in (1.0, -1.0):

#             for z_pos in (
#                 tooth_edge_margin,
#                 clamp_depth - tooth_edge_margin
#             ):

#                 edge = one_way_clamp.edges(
#                     cq.selectors.NearestToPointSelector(
#                         (
#                             x_sign * x_apex,
#                             y_pos,
#                             z_pos
#                         )
#                     )
#                 )

#                 edge_vals = edge.vals()

#                 if len(edge_vals) != 1:
#                     raise ValueError(
#                         f"Could not uniquely select tooth edge at "
#                         f"({x_sign * x_apex}, {y_pos}, {z_pos})."
#                     )

#                 tooth_edges.append(edge_vals[0])

#     if len(tooth_edges) != 12:
#         raise ValueError(
#             f"Expected 12 tooth edges, found {len(tooth_edges)}."
#         )

#     one_way_clamp = (
#         one_way_clamp
#         .newObject(tooth_edges)
#         .fillet(tooth_fillet_radius)
#     )

#     return one_way_clamp


# # ==============================================================================
# # TWO-WAY CONNECTOR
# # ==============================================================================

# def make_2_way_connector(
#     stick_width=stick_width,
#     stick_thickness=stick_thickness,
#     clearance=clearance,
#     wall_thickness=wall_thickness,
#     base_thickness=base_thickness,
#     overall_height=overall_height,
#     overall_outer_curve_height=overall_outer_curve_height,
#     overall_inner_curve_height=overall_inner_curve_height,
#     snap_lip_inward=snap_lip_inward,
#     tip_fillet_radius=tip_fillet_radius,
#     pocket_fillet_radius=pocket_fillet_radius,
#     wall_arm_fillet_radius=wall_arm_fillet_radius,
#     tooth_fillet_radius=tooth_fillet_radius,
#     front_back_wall_height=front_back_wall_height,
#     tooth_edge_margin=tooth_edge_margin,
# ):

#     one_way = make_one_way_connector(
#         stick_width=stick_width,
#         stick_thickness=stick_thickness,
#         clearance=clearance,
#         wall_thickness=wall_thickness,
#         base_thickness=base_thickness,
#         overall_height=overall_height,
#         overall_outer_curve_height=overall_outer_curve_height,
#         overall_inner_curve_height=overall_inner_curve_height,
#         snap_lip_inward=snap_lip_inward,
#         tip_fillet_radius=tip_fillet_radius,
#         pocket_fillet_radius=pocket_fillet_radius,
#         wall_arm_fillet_radius=wall_arm_fillet_radius,
#         tooth_fillet_radius=tooth_fillet_radius,
#         front_back_wall_height=front_back_wall_height,
#         tooth_edge_margin=tooth_edge_margin,
#     )

#     opposite_way = one_way.mirror("XZ")

#     return one_way.union(opposite_way)


# # ==============================================================================
# # OUTER ARM EDGE SELECTOR
# #
# # Selects the 8 outer arm perimeter edges.
# # Does NOT fillet them automatically.
# # ==============================================================================

# def select_outer_arm_edges(
#     result,
#     outer_x,
#     x_c,
#     y_c,
#     R_o,
#     mid_y,
#     theta_outer,
#     clamp_depth,
# ):
#     """
#     Select:

#         - left/right straight outer arm edges
#         - left/right outer curved arm edges

#     on both Z side faces.

#     The short front/back cover termination edges are excluded.
#     """

#     # --------------------------------------------------------------------------
#     # Points on straight outer edges
#     # --------------------------------------------------------------------------

#     straight_y = mid_y / 2.0

#     points = [
#         # Z = 0
#         (outer_x, straight_y, 0.0),
#         (-outer_x, straight_y, 0.0),

#         # Z = clamp_depth
#         (outer_x, straight_y, clamp_depth),
#         (-outer_x, straight_y, clamp_depth),
#     ]

#     # --------------------------------------------------------------------------
#     # Points on outer circular edges
#     # --------------------------------------------------------------------------

#     outer_mid_x = (
#         x_c
#         + R_o * math.cos(theta_outer / 2.0)
#     )

#     outer_mid_y = (
#         y_c
#         + R_o * math.sin(theta_outer / 2.0)
#     )

#     points += [
#         # Z = 0
#         (outer_mid_x, outer_mid_y, 0.0),
#         (-outer_mid_x, outer_mid_y, 0.0),

#         # Z = clamp_depth
#         (outer_mid_x, outer_mid_y, clamp_depth),
#         (-outer_mid_x, outer_mid_y, clamp_depth),
#     ]

#     # --------------------------------------------------------------------------
#     # Select exactly one edge near each calculated point
#     # --------------------------------------------------------------------------

#     selected = []

#     for point in points:

#         edges = result.edges(
#             cq.selectors.NearestToPointSelector(point)
#         )

#         if len(edges.vals()) != 1:
#             raise ValueError(
#                 f"Expected one edge near {point}, "
#                 f"found {len(edges.vals())}."
#             )

#         selected.append(
#             edges.vals()[0]
#         )

#     return result.newObject(selected)


# # ==============================================================================
# # HELPER FOR CURRENT DEFAULT GEOMETRY
# # ==============================================================================

# def select_current_outer_arm_edges(result):

#     gap_width = (
#         stick_thickness
#         + clearance
#     )

#     half_gap = gap_width / 2.0

#     outer_x = (
#         half_gap
#         + wall_thickness
#     )

#     clamp_depth = (
#         stick_width
#         + clearance
#         + 2.0 * wall_thickness
#     )

#     straight_height = (
#         overall_height
#         - base_thickness
#         - overall_outer_curve_height
#     )

#     mid_y = (
#         base_thickness
#         + straight_height
#     )

#     R_o = (
#         overall_outer_curve_height**2
#         + snap_lip_inward**2
#     ) / (
#         2.0 * snap_lip_inward
#     )

#     x_c = outer_x - R_o
#     y_c = mid_y

#     theta_outer = math.asin(
#         overall_outer_curve_height / R_o
#     )

#     return select_outer_arm_edges(
#         result,
#         outer_x,
#         x_c,
#         y_c,
#         R_o,
#         mid_y,
#         theta_outer,
#         clamp_depth,
#     )


# # ==============================================================================
# # STL EXPORT
# # ==============================================================================

# def export_stl(
#     result,
#     filename="popsicle_connector.stl"
# ):

#     cq.exporters.export(
#         result,
#         filename,
#         cq.exporters.ExportTypes.STL,
#         tolerance=0.01,
#         angularTolerance=0.1
#     )

import cadquery as cq
import math


# ==============================================================================
# DEFAULT PARAMETERS
# ==============================================================================

stick_width = 9.10
stick_thickness = 1.90
clearance = 0.10

pocket_thick = stick_thickness + clearance
pocket_width = stick_width + clearance

wall_thickness = 1.2
base_thickness = 2.0
overall_height = 13.6

overall_outer_curve_height = 4.6
overall_inner_curve_height = 4.0
snap_lip_inward = 0.35

tip_fillet_radius = 0.30
pocket_fillet_radius = 0.30
wall_arm_fillet_radius = 0.30
tooth_fillet_radius = 0.15

front_back_wall_height = 6.69

# Teeth stop this distance short of both Z-side edges
tooth_edge_margin = 0.50


# ==============================================================================
# OUTER ARM EDGE SELECTOR
# ==============================================================================

def select_outer_arm_edges(
    result,
    outer_x,
    x_c,
    y_c,
    R_o,
    mid_y,
    theta_outer,
    clamp_depth,
):
    """
    Select the 8 outer arm perimeter edges:

        - 4 straight outer edges
        - 4 outer curved edges

    on both Z side faces.

    The short front/back cover termination edges are excluded.
    """

    straight_y = mid_y / 2.0

    points = [
        # Straight outer edges
        ( outer_x, straight_y, 0.0),
        (-outer_x, straight_y, 0.0),
        ( outer_x, straight_y, clamp_depth),
        (-outer_x, straight_y, clamp_depth),
    ]

    # Outer circular edge midpoint
    outer_mid_x = (
        x_c
        + R_o * math.cos(theta_outer / 2.0)
    )

    outer_mid_y = (
        y_c
        + R_o * math.sin(theta_outer / 2.0)
    )

    points += [
        # Curved outer edges
        ( outer_mid_x, outer_mid_y, 0.0),
        (-outer_mid_x, outer_mid_y, 0.0),
        ( outer_mid_x, outer_mid_y, clamp_depth),
        (-outer_mid_x, outer_mid_y, clamp_depth),
    ]

    selected = []

    for point in points:

        edges = result.edges(
            cq.selectors.NearestToPointSelector(point)
        )

        edge_vals = edges.vals()

        if len(edge_vals) != 1:
            raise ValueError(
                f"Expected one edge near {point}, "
                f"found {len(edge_vals)}."
            )

        selected.append(edge_vals[0])

    return result.newObject(selected)


# ==============================================================================
# ONE-WAY CONNECTOR
# ==============================================================================

def make_one_way_connector(
    stick_width=stick_width,
    stick_thickness=stick_thickness,
    clearance=clearance,
    wall_thickness=wall_thickness,
    base_thickness=base_thickness,
    overall_height=overall_height,
    overall_outer_curve_height=overall_outer_curve_height,
    overall_inner_curve_height=overall_inner_curve_height,
    snap_lip_inward=snap_lip_inward,
    tip_fillet_radius=tip_fillet_radius,
    pocket_fillet_radius=pocket_fillet_radius,
    wall_arm_fillet_radius=wall_arm_fillet_radius,
    tooth_fillet_radius=tooth_fillet_radius,
    front_back_wall_height=front_back_wall_height,
    tooth_edge_margin=tooth_edge_margin,
    export=False,
    filename="popsicle_one_way.stl",
):

    # --------------------------------------------------------------------------
    # Basic dimensions
    # --------------------------------------------------------------------------

    pocket_thick = stick_thickness + clearance
    pocket_width = stick_width + clearance

    clamp_depth = (
        pocket_width
        + 2.0 * wall_thickness
    )

    gap_width = pocket_thick
    half_gap = gap_width / 2.0
    outer_x = half_gap + wall_thickness

    straight_height = (
        overall_height
        - base_thickness
        - overall_outer_curve_height
    )

    if straight_height <= 0:
        raise ValueError(
            "overall_height is too small for the selected curve height."
        )

    mid_y = base_thickness + straight_height

    # --------------------------------------------------------------------------
    # Outer arc
    # --------------------------------------------------------------------------

    if snap_lip_inward <= 0:
        raise ValueError(
            "snap_lip_inward must be greater than zero."
        )

    R_o = (
        overall_outer_curve_height**2
        + snap_lip_inward**2
    ) / (
        2.0 * snap_lip_inward
    )

    x_c = outer_x - R_o
    y_c = mid_y

    sin_theta_outer = (
        overall_outer_curve_height / R_o
    )

    if not -1.0 <= sin_theta_outer <= 1.0:
        raise ValueError(
            "Invalid outer arc geometry."
        )

    theta_outer = math.asin(sin_theta_outer)

    outer_tip_x = (
        x_c
        + R_o * math.cos(theta_outer)
    )

    outer_tip_y = (
        y_c
        + overall_outer_curve_height
    )

    # --------------------------------------------------------------------------
    # Inner arc
    # --------------------------------------------------------------------------

    R_i = R_o - wall_thickness

    if R_i <= 0:
        raise ValueError(
            "Wall thickness is too large for the calculated inner radius."
        )

    sin_theta_inner = (
        overall_inner_curve_height / R_i
    )

    if not -1.0 <= sin_theta_inner <= 1.0:
        raise ValueError(
            "Invalid inner arc geometry."
        )

    theta_inner = math.asin(sin_theta_inner)

    inner_tip_x = (
        x_c
        + R_i * math.cos(theta_inner)
    )

    inner_tip_y = (
        y_c
        + overall_inner_curve_height
    )

    # --------------------------------------------------------------------------
    # Arc midpoints
    # --------------------------------------------------------------------------

    outer_mid_x = (
        x_c
        + R_o * math.cos(theta_outer / 2.0)
    )

    outer_mid_y = (
        y_c
        + R_o * math.sin(theta_outer / 2.0)
    )

    inner_mid_x = (
        x_c
        + R_i * math.cos(theta_inner / 2.0)
    )

    inner_mid_y = (
        y_c
        + R_i * math.sin(theta_inner / 2.0)
    )

    # --------------------------------------------------------------------------
    # Build one half
    # --------------------------------------------------------------------------

    half_clamp = (
        cq.Workplane("XY")
        .moveTo(0, 0)
        .lineTo(outer_x, 0)
        .lineTo(outer_x, mid_y)
        .threePointArc(
            (outer_mid_x, outer_mid_y),
            (outer_tip_x, outer_tip_y)
        )
        .lineTo(
            inner_tip_x,
            inner_tip_y
        )
        .threePointArc(
            (inner_mid_x, inner_mid_y),
            (half_gap, mid_y)
        )
        .lineTo(
            half_gap,
            base_thickness
        )
        .lineTo(
            0,
            base_thickness
        )
        .close()
        .extrude(clamp_depth)
    )

    # --------------------------------------------------------------------------
    # Tip fillets
    # --------------------------------------------------------------------------

    def tip_edge_selector(x, y):
        eps = 0.05

        return cq.selectors.BoxSelector(
            (
                x - eps,
                y - eps,
                0
            ),
            (
                x + eps,
                y + eps,
                clamp_depth
            )
        )

    half_clamp = (
        half_clamp
        .edges(
            tip_edge_selector(
                outer_tip_x,
                outer_tip_y
            )
        )
        .fillet(
            tip_fillet_radius
        )
    )

    half_clamp = (
        half_clamp
        .edges(
            tip_edge_selector(
                inner_tip_x,
                inner_tip_y
            )
        )
        .fillet(
            tip_fillet_radius
        )
    )

    # --------------------------------------------------------------------------
    # Mirror left/right
    # --------------------------------------------------------------------------

    one_way_clamp = half_clamp.union(
        half_clamp.mirror("YZ")
    )

    # --------------------------------------------------------------------------
    # Front/back pocket walls
    # --------------------------------------------------------------------------

    pocket_center_y = (
        base_thickness
        + front_back_wall_height / 2.0
    )

    back_wall = (
        cq.Workplane("XY")
        .moveTo(
            0,
            pocket_center_y
        )
        .rect(
            gap_width,
            front_back_wall_height
        )
        .extrude(
            wall_thickness
        )
    )

    front_wall = (
        cq.Workplane("XY")
        .workplane(
            offset=clamp_depth - wall_thickness
        )
        .moveTo(
            0,
            pocket_center_y
        )
        .rect(
            gap_width,
            front_back_wall_height
        )
        .extrude(
            wall_thickness
        )
    )

    pocket_walls = (
        back_wall.union(front_wall)
    )

    one_way_clamp = (
        one_way_clamp.union(
            pocket_walls
        )
    )

    # --------------------------------------------------------------------------
    # Pocket fillets
    # --------------------------------------------------------------------------

    eps = 0.03

    wall_y_bottom = base_thickness

    wall_y_top = (
        base_thickness
        + front_back_wall_height
    )

    for x_pos in (
        half_gap,
        -half_gap
    ):

        for z_pos in (
            wall_thickness,
            clamp_depth - wall_thickness
        ):

            selector = cq.selectors.BoxSelector(
                (
                    x_pos - eps,
                    wall_y_bottom - eps,
                    z_pos - eps
                ),
                (
                    x_pos + eps,
                    wall_y_top + eps,
                    z_pos + eps
                )
            )

            one_way_clamp = (
                one_way_clamp
                .edges(selector)
                .fillet(
                    pocket_fillet_radius
                )
            )

    # --------------------------------------------------------------------------
    # Cover / arm junction fillets
    #
    # These are the 4 fillets where the front/back covers meet the arms.
    # --------------------------------------------------------------------------

    side_eps = 0.04

    wall_top_y = (
        base_thickness
        + front_back_wall_height
    )

    for x_pos in (
        half_gap,
        -half_gap
    ):

        # Front cover / arm junction
        front_selector = cq.selectors.BoxSelector(
            (
                x_pos - side_eps,
                wall_top_y - side_eps,
                -side_eps
            ),
            (
                x_pos + side_eps,
                wall_top_y + side_eps,
                wall_thickness + side_eps
            )
        )

        one_way_clamp = (
            one_way_clamp
            .edges(front_selector)
            .fillet(
                wall_arm_fillet_radius
            )
        )

        # Back cover / arm junction
        back_selector = cq.selectors.BoxSelector(
            (
                x_pos - side_eps,
                wall_top_y - side_eps,
                clamp_depth
                - wall_thickness
                - side_eps
            ),
            (
                x_pos + side_eps,
                wall_top_y + side_eps,
                clamp_depth + side_eps
            )
        )

        one_way_clamp = (
            one_way_clamp
            .edges(back_selector)
            .fillet(
                wall_arm_fillet_radius
            )
        )

    # --------------------------------------------------------------------------
    # Conformal internal friction teeth
    #
    # Teeth stop tooth_edge_margin short of both Z-side edges.
    # --------------------------------------------------------------------------

    def get_inner_x(y_val):

        dy = y_val - y_c

        value = (
            R_i**2
            - dy**2
        )

        if value < 0:
            raise ValueError(
                "Tooth position lies outside inner arc."
            )

        return (
            x_c
            + math.sqrt(value)
        )

    ridge_ys = [
        10.2,
        11.2,
        12.2
    ]

    prot = 0.20
    tooth_half = 0.35

    tooth_depth = (
        clamp_depth
        - 2.0 * tooth_edge_margin
    )

    if tooth_depth <= 0:
        raise ValueError(
            "tooth_edge_margin is too large."
        )

    for y_pos in ridge_ys:

        y_bot = y_pos - tooth_half
        y_top = y_pos + tooth_half

        x_bot = get_inner_x(y_bot)
        x_top = get_inner_x(y_top)
        x_mid = get_inner_x(y_pos)

        x_apex = x_mid - prot

        right_tooth = (
            cq.Workplane("XY")
            .moveTo(
                x_bot + 0.05,
                y_bot
            )
            .lineTo(
                x_bot,
                y_bot
            )
            .threePointArc(
                (x_apex, y_pos),
                (x_top, y_top)
            )
            .lineTo(
                x_top + 0.05,
                y_top
            )
            .threePointArc(
                (x_mid + 0.05, y_pos),
                (x_bot + 0.05, y_bot)
            )
            .close()
            .extrude(
                tooth_depth
            )
            .translate(
                (
                    0,
                    0,
                    tooth_edge_margin
                )
            )
        )

        one_way_clamp = (
            one_way_clamp
            .union(right_tooth)
            .union(
                right_tooth.mirror("YZ")
            )
        )

    # --------------------------------------------------------------------------
    # Tooth front/back edge fillets
    #
    # 3 teeth × 2 sides × 2 Z faces = 12 edges.
    #
    # Applied AFTER the teeth are fused to the clamp.
    # --------------------------------------------------------------------------

    tooth_edges = []

    for y_pos in ridge_ys:

        x_mid = get_inner_x(y_pos)
        x_apex = x_mid - prot

        for x_sign in (
            1.0,
            -1.0
        ):

            for z_pos in (
                tooth_edge_margin,
                clamp_depth - tooth_edge_margin
            ):

                edge_wp = one_way_clamp.edges(
                    cq.selectors.NearestToPointSelector(
                        (
                            x_sign * x_apex,
                            y_pos,
                            z_pos
                        )
                    )
                )

                edge_vals = edge_wp.vals()

                if len(edge_vals) != 1:
                    raise ValueError(
                        f"Could not uniquely select tooth edge at "
                        f"({x_sign * x_apex}, {y_pos}, {z_pos})."
                    )

                tooth_edges.append(
                    edge_vals[0]
                )

    if len(tooth_edges) != 12:
        raise ValueError(
            f"Expected 12 tooth edges, found {len(tooth_edges)}."
        )

    one_way_clamp = (
        one_way_clamp
        .newObject(tooth_edges)
        .fillet(
            tooth_fillet_radius
        )
    )

    # --------------------------------------------------------------------------
    # OUTER ARM FILLET
    #
    # This is the 8-edge fillet that was previously done manually in Jupyter.
    # It is now part of the core connector function.
    # --------------------------------------------------------------------------

    if wall_arm_fillet_radius > 0:

        outer_arm_edges = select_outer_arm_edges(
            one_way_clamp,
            outer_x,
            x_c,
            y_c,
            R_o,
            mid_y,
            theta_outer,
            clamp_depth,
        )

        one_way_clamp = (
            outer_arm_edges
            .fillet(
                wall_arm_fillet_radius
            )
        )

    # --------------------------------------------------------------------------
    # Optional STL export
    # --------------------------------------------------------------------------

    if export:

        cq.exporters.export(
            one_way_clamp,
            filename,
            cq.exporters.ExportTypes.STL,
            tolerance=0.01,
            angularTolerance=0.1
        )

    return one_way_clamp


# ==============================================================================
# TWO-WAY CONNECTOR
#
# Second one-way connector is mirrored 180 degrees through the XZ plane.
# Same virtual center.
# ==============================================================================

def make_2_way_connector(
    stick_width=stick_width,
    stick_thickness=stick_thickness,
    clearance=clearance,
    wall_thickness=wall_thickness,
    base_thickness=base_thickness,
    overall_height=overall_height,
    overall_outer_curve_height=overall_outer_curve_height,
    overall_inner_curve_height=overall_inner_curve_height,
    snap_lip_inward=snap_lip_inward,
    tip_fillet_radius=tip_fillet_radius,
    pocket_fillet_radius=pocket_fillet_radius,
    wall_arm_fillet_radius=wall_arm_fillet_radius,
    tooth_fillet_radius=tooth_fillet_radius,
    front_back_wall_height=front_back_wall_height,
    tooth_edge_margin=tooth_edge_margin,
    export=False,
    filename="popsicle_2way.stl",
):

    one_way = make_one_way_connector(
        stick_width=stick_width,
        stick_thickness=stick_thickness,
        clearance=clearance,
        wall_thickness=wall_thickness,
        base_thickness=base_thickness,
        overall_height=overall_height,
        overall_outer_curve_height=overall_outer_curve_height,
        overall_inner_curve_height=overall_inner_curve_height,
        snap_lip_inward=snap_lip_inward,
        tip_fillet_radius=tip_fillet_radius,
        pocket_fillet_radius=pocket_fillet_radius,
        wall_arm_fillet_radius=wall_arm_fillet_radius,
        tooth_fillet_radius=tooth_fillet_radius,
        front_back_wall_height=front_back_wall_height,
        tooth_edge_margin=tooth_edge_margin,
        export=False,
    )

    opposite_way = one_way.mirror("XZ")

    result = one_way.union(
        opposite_way
    )

    # --------------------------------------------------------------------------
    # Optional STL export
    # --------------------------------------------------------------------------

    if export:

        cq.exporters.export(
            result,
            filename,
            cq.exporters.ExportTypes.STL,
            tolerance=0.01,
            angularTolerance=0.1
        )

    return result


# ==============================================================================
# L CONNECTOR
#
# Two identical one-way connectors sharing the same virtual center,
# with the second rotated 90 degrees around the Z axis.
#
# First connector: +Y direction
# Second connector: -X direction
# ==============================================================================

def make_L_connector(
    stick_width=stick_width,
    stick_thickness=stick_thickness,
    clearance=clearance,
    wall_thickness=wall_thickness,
    base_thickness=base_thickness,
    overall_height=overall_height,
    overall_outer_curve_height=overall_outer_curve_height,
    overall_inner_curve_height=overall_inner_curve_height,
    snap_lip_inward=snap_lip_inward,
    tip_fillet_radius=tip_fillet_radius,
    pocket_fillet_radius=pocket_fillet_radius,
    wall_arm_fillet_radius=wall_arm_fillet_radius,
    tooth_fillet_radius=tooth_fillet_radius,
    front_back_wall_height=front_back_wall_height,
    tooth_edge_margin=tooth_edge_margin,
    export=False,
    filename="popsicle_L.stl",
):

    one_way = make_one_way_connector(
        stick_width=stick_width,
        stick_thickness=stick_thickness,
        clearance=clearance,
        wall_thickness=wall_thickness,
        base_thickness=base_thickness,
        overall_height=overall_height,
        overall_outer_curve_height=overall_outer_curve_height,
        overall_inner_curve_height=overall_inner_curve_height,
        snap_lip_inward=snap_lip_inward,
        tip_fillet_radius=tip_fillet_radius,
        pocket_fillet_radius=pocket_fillet_radius,
        wall_arm_fillet_radius=wall_arm_fillet_radius,
        tooth_fillet_radius=tooth_fillet_radius,
        front_back_wall_height=front_back_wall_height,
        tooth_edge_margin=tooth_edge_margin,
        export=False,
    )

    rotated_way = one_way.rotate(
        (0, 0, 0),
        (0, 0, 1),
        90
    )

    result = one_way.union(
        rotated_way
    )

    # --------------------------------------------------------------------------
    # Optional STL export
    # --------------------------------------------------------------------------

    if export:

        cq.exporters.export(
            result,
            filename,
            cq.exporters.ExportTypes.STL,
            tolerance=0.01,
            angularTolerance=0.1
        )

    return result


# ==============================================================================
# HELPER FOR SELECTING CURRENT DEFAULT OUTER ARM EDGES
#
# Kept for compatibility/testing. Normally you no longer need this because
# make_one_way_connector() already applies the outer-arm fillet.
# ==============================================================================

def select_current_outer_arm_edges(result):

    gap_width = (
        stick_thickness
        + clearance
    )

    half_gap = gap_width / 2.0

    outer_x = (
        half_gap
        + wall_thickness
    )

    clamp_depth = (
        stick_width
        + clearance
        + 2.0 * wall_thickness
    )

    straight_height = (
        overall_height
        - base_thickness
        - overall_outer_curve_height
    )

    mid_y = (
        base_thickness
        + straight_height
    )

    R_o = (
        overall_outer_curve_height**2
        + snap_lip_inward**2
    ) / (
        2.0 * snap_lip_inward
    )

    x_c = outer_x - R_o
    y_c = mid_y

    theta_outer = math.asin(
        overall_outer_curve_height / R_o
    )

    return select_outer_arm_edges(
        result,
        outer_x,
        x_c,
        y_c,
        R_o,
        mid_y,
        theta_outer,
        clamp_depth,
    )