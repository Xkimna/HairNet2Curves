import bpy
from mathutils import Vector


def new_Surface_Deform_GeoNode_Group():
    node_group = bpy.data.node_groups.new('Surface Deform', 'GeometryNodeTree')
    inNode = node_group.nodes.new('NodeGroupInput')
    node_group.outputs.new('NodeSocketGeometry', 'Geometry')
    outNode = node_group.nodes.new('NodeGroupOutput')
    node_group.inputs.new('NodeSocketGeometry', 'Geometry')
    node = node_group.nodes.new(type='GeometryNodeDeformCurvesOnSurface')
    node_group.links.new(inNode.outputs['Geometry'], node.inputs['Curves'])
    node_group.links.new(node.outputs['Curves'], outNode.inputs['Geometry'])
    inNode.location = Vector((-1.5 * inNode.width, 0))
    outNode.location = Vector((1.5 * outNode.width, 0))
    return node_group


def new_Rest_Position_GeoNode_Group():
    node_group = bpy.data.node_groups.new('HairNet Rest Position', 'GeometryNodeTree')
    inNode = node_group.nodes.new('NodeGroupInput')
    node_group.outputs.new('NodeSocketGeometry', 'Geometry')
    outNode = node_group.nodes.new('NodeGroupOutput')
    node_group.inputs.new('NodeSocketGeometry', 'Geometry')
    store_named_attribute_node = node_group.nodes.new(type='GeometryNodeStoreNamedAttribute')
    store_named_attribute_node.data_type = 'FLOAT_VECTOR'
    store_named_attribute_node.inputs[2].default_value = "rest_position"
    position_node = node_group.nodes.new(type='GeometryNodeInputPosition')
    node_group.links.new(inNode.outputs['Geometry'], store_named_attribute_node.inputs['Geometry'])
    node_group.links.new(position_node.outputs['Position'], store_named_attribute_node.inputs['Value'])
    node_group.links.new(store_named_attribute_node.outputs['Geometry'], outNode.inputs['Geometry'])
    inNode.location = Vector((-1.5 * inNode.width, 0))
    outNode.location = Vector((1.5 * outNode.width, 0))
    position_node.location = Vector((-1.5 * position_node.width, - 1.5 * position_node.height))
    return node_group


def new_Interspersed_Restoration_GeoNode_Group():
    node_group = bpy.data.node_groups.new('HairNet Interspersed Restoration', 'GeometryNodeTree')

    # input & output
    input_node = node_group.nodes.new('NodeGroupInput')
    node_group.inputs.new('NodeSocketGeometry', 'Geometry')
    input_socket = node_group.inputs.new('NodeSocketObject', 'Head Object')
    input_socket.default_value = bpy.context.object.head_object
    input_socket2 = node_group.inputs.new('NodeSocketFloat', 'Intensity')
    input_socket2.default_value = 0.15
    input_socket3 = node_group.inputs.new('NodeSocketFloat', 'Blur Iterations')
    input_socket3.default_value = 20
    input_socket4 = node_group.inputs.new('NodeSocketFloat', 'Fluffy Position')
    input_socket4.default_value = 4.6
    input_socket5 = node_group.inputs.new('NodeSocketFloat', 'Fluffy Intensity')
    input_socket5.default_value = 0.04
    output_node = node_group.nodes.new('NodeGroupOutput')
    node_group.outputs.new('NodeSocketGeometry', 'Geometry')

    width = input_node.width
    height = input_node.height
    input_node.location = Vector((-7.5 * width, 0))
    output_node.location = Vector((43.0 * width, -4.5 * height))

    # Judges Interspersed
    frame_jin = node_group.nodes.new("NodeFrame")
    frame_jin.label = "Judges Interspersed"
    object_info_node = node_group.nodes.new(type='GeometryNodeObjectInfo')
    object_info_node.transform_space = 'RELATIVE'
    object_info_node.parent = frame_jin
    position_node = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node.parent = frame_jin
    geometry_proximity_node = node_group.nodes.new(type='GeometryNodeProximity')
    geometry_proximity_node.target_element = 'FACES'
    geometry_proximity_node.parent = frame_jin
    subtract_node = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node.operation = 'SUBTRACT'
    subtract_node.parent = frame_jin
    normal_node = node_group.nodes.new(type='GeometryNodeInputNormal')
    normal_node.parent = frame_jin
    capture_attribute_node = node_group.nodes.new(type='GeometryNodeCaptureAttribute')
    capture_attribute_node.data_type = 'FLOAT_VECTOR'
    capture_attribute_node.parent = frame_jin
    sample_nearest_surface_node_2 = node_group.nodes.new(type='GeometryNodeSampleNearestSurface')
    sample_nearest_surface_node_2.data_type = 'FLOAT_VECTOR'
    sample_nearest_surface_node_2.parent = frame_jin
    greater_than_node = node_group.nodes.new(type='FunctionNodeCompare')
    greater_than_node.data_type = 'VECTOR'
    greater_than_node.mode = 'DOT_PRODUCT'
    greater_than_node.inputs[10].default_value = 0.0
    greater_than_node.parent = frame_jin

    object_info_node.location = Vector((-6.0 * width, 0))
    position_node.location = Vector((-4.5 * width, -1.5 * height))
    geometry_proximity_node.location = Vector((-3.0 * width, -1.5 * height))
    subtract_node.location = Vector((-1.5 * width, -1.5 * height))
    normal_node.location = Vector((-4.5 * width, 1.5 * height))
    capture_attribute_node.location = Vector((-3.0 * width, 1.5 * height))
    sample_nearest_surface_node_2.location = Vector((-1.5 * width, 1.5 * height))

    # main
    input_node_2 = node_group.nodes.new('NodeGroupInput')
    position_node_2 = node_group.nodes.new(type='GeometryNodeInputPosition')
    capture_attribute_node_2 = node_group.nodes.new(type='GeometryNodeCaptureAttribute')
    capture_attribute_node_2.data_type = 'FLOAT_VECTOR'
    store_named_attribute_node = node_group.nodes.new(type='GeometryNodeStoreNamedAttribute')
    store_named_attribute_node.data_type = 'BOOLEAN'
    store_named_attribute_node.inputs[2].default_value = "is_interspersed"
    store_named_attribute_node_2 = node_group.nodes.new(type='GeometryNodeStoreNamedAttribute')
    store_named_attribute_node_2.inputs[2].default_value = "distance"
    set_position_node = node_group.nodes.new(type='GeometryNodeSetPosition')
    resample_node = node_group.nodes.new(type='GeometryNodeResampleCurve')
    resample_node.inputs[2].default_value = 100
    set_position_node_2 = node_group.nodes.new(type='GeometryNodeSetPosition')
    set_position_node_3 = node_group.nodes.new(type='GeometryNodeSetPosition')
    set_position_node_4 = node_group.nodes.new(type='GeometryNodeSetPosition')
    set_position_node_5 = node_group.nodes.new(type='GeometryNodeSetPosition')

    input_node_2.location = Vector((-7.5 * width, -5.0 * height))
    position_node_2.location = Vector((-7.5 * width, -7.0 * height))
    capture_attribute_node_2.location = Vector((-6.0 * width, -5.0 * height))
    store_named_attribute_node.location = Vector((1.5 * width, -4.5 * height))
    store_named_attribute_node_2.location = Vector((3.0 * width, -4.5 * height))
    set_position_node.location = Vector((5.0 * width, -4.5 * height))
    resample_node.location = Vector((6.5 * width, -4.5 * height))
    set_position_node_2.location = Vector((18.5 * width, -4.5 * height))
    set_position_node_3.location = Vector((24.5 * width, -4.5 * height))
    set_position_node_4.location = Vector((27.5 * width, -4.5 * height))
    set_position_node_5.location = Vector((41.0 * width, -4.5 * height))

    # move on surface
    frame_mos = node_group.nodes.new("NodeFrame")
    frame_mos.label = "Move on Surface"
    raycast_node = node_group.nodes.new(type='GeometryNodeRaycast')
    raycast_node.parent = frame_mos
    position_node_3 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_3.parent = frame_mos
    subtract_node_2 = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node_2.operation = 'SUBTRACT'
    subtract_node_2.parent = frame_mos
    combine_node = node_group.nodes.new(type='ShaderNodeCombineXYZ')
    combine_node.parent = frame_mos
    separate_node = node_group.nodes.new(type='ShaderNodeSeparateXYZ')
    separate_node.parent = frame_mos
    separate_node_2 = node_group.nodes.new(type='ShaderNodeSeparateXYZ')
    separate_node_2.parent = frame_mos
    position_node_4 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_4.parent = frame_mos
    object_info_node_2 = node_group.nodes.new(type='GeometryNodeObjectInfo')
    object_info_node_2.transform_space = 'RELATIVE'
    object_info_node_2.parent = frame_mos
    input_node_3 = node_group.nodes.new('NodeGroupInput')
    input_node_3.parent = frame_mos

    raycast_node.location = Vector((3.0 * width, -9.0 * height))
    position_node_3.location = Vector((1.5 * width, -10.5 * height))
    subtract_node_2.location = Vector((1.5 * width, -11.5 * height))
    combine_node.location = Vector((0, -11.5 * height))
    separate_node.location = Vector((-1.5 * width, -9.5 * height))
    separate_node_2.location = Vector((-1.5 * width, -11 * height))
    position_node_4.location = Vector((-3.0 * width, -9.5 * height))
    object_info_node_2.location = Vector((-3.0 * width, -10.5 * height))
    input_node_3.location = Vector((-4.5 * width, -10.5 * height))

    # not select root
    frame_rs = node_group.nodes.new("NodeFrame")
    frame_rs.label = "Not Root Select"
    endpoint_selection_node = node_group.nodes.new(type='GeometryNodeCurveEndpointSelection')
    endpoint_selection_node.inputs[0].default_value = 1
    endpoint_selection_node.inputs[1].default_value = 0
    endpoint_selection_node.parent = frame_rs
    not_node = node_group.nodes.new(type='FunctionNodeBooleanMath')
    not_node.operation = 'NOT'
    not_node.parent = frame_rs
    named_attribute_node = node_group.nodes.new(type='GeometryNodeInputNamedAttribute')
    named_attribute_node.data_type = 'BOOLEAN'
    named_attribute_node.inputs[0].default_value = 'is_interspersed'
    named_attribute_node.parent = frame_rs
    and_node = node_group.nodes.new(type='FunctionNodeBooleanMath')
    and_node.operation = 'AND'
    and_node.parent = frame_rs

    endpoint_selection_node.location = Vector((2.0 * width, 0))
    not_node.location = Vector((3.5 * width, 0))
    named_attribute_node.location = Vector((2.0 * width, -1.5 * height))
    and_node.location = Vector((3.5 * width, -1.5 * height))

    # Blurred Position Attribute
    frame_bpa = node_group.nodes.new("NodeFrame")
    frame_bpa.label = "Blurred Position Attribute"
    frame_rp = node_group.nodes.new("NodeFrame")
    frame_rp.label = "Root Pinning"
    frame_rp.parent = frame_bpa
    spline_parameter_node = node_group.nodes.new(type='GeometryNodeSplineParameter')
    spline_parameter_node.parent = frame_bpa
    multiply_node = node_group.nodes.new(type='ShaderNodeMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.parent = frame_bpa
    input_node_4 = node_group.nodes.new('NodeGroupInput')
    input_node_4.parent = frame_bpa
    position_node_5 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_5.parent = frame_bpa
    blur_attribute_node = node_group.nodes.new(type='GeometryNodeBlurAttribute')
    blur_attribute_node.data_type = 'FLOAT_VECTOR'
    blur_attribute_node.parent = frame_bpa
    point_of_curve_node = node_group.nodes.new(type='GeometryNodePointsOfCurve')
    point_of_curve_node.parent = frame_rp
    evaluate_on_domain_node = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node.data_type = 'INT'
    evaluate_on_domain_node.domain = 'CURVE'
    evaluate_on_domain_node.parent = frame_rp
    evaluate_at_index_node = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node.parent = frame_rp
    evaluate_at_index_node_2 = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node_2.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node_2.parent = frame_rp
    subtract_node_3 = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node_3.operation = 'SUBTRACT'
    subtract_node_3.parent = frame_rp
    subtract_node_4 = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node_4.operation = 'SUBTRACT'
    subtract_node_4.parent = frame_rp
    subtract_node_5 = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node_5.operation = 'SUBTRACT'
    subtract_node_5.parent = frame_rp
    position_node_6 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_6.parent = frame_rp

    spline_parameter_node.location = Vector((6.5 * width, -1.5 * height))
    multiply_node.location = Vector((8.0 * width, -1.5 * height))
    input_node_4.location = Vector((8.0 * width, 0.5 * height))
    position_node_5.location = Vector((8.0 * width, 1.5 * height))
    blur_attribute_node.location = Vector((9.5 * width, height))
    point_of_curve_node.location = Vector((11.0 * width, 0.5 * height))
    evaluate_on_domain_node.location = Vector((11.0 * width, -1.0 * height))
    evaluate_at_index_node.location = Vector((12.5 * width, height))
    evaluate_at_index_node_2.location = Vector((12.5 * width, -0.5 * height))
    subtract_node_3.location = Vector((14.0 * width, -0.5 * height))
    subtract_node_4.location = Vector((15.5 * width, height))
    subtract_node_5.location = Vector((17.0 * width, height))
    position_node_6.location = Vector((15.5 * width, -1.0 * height))

    # Offset
    frame_offset = node_group.nodes.new("NodeFrame")
    frame_offset.label = "OFFSET"
    spline_parameter_node_2 = node_group.nodes.new(type='GeometryNodeSplineParameter')
    spline_parameter_node_2.parent = frame_offset
    input_node_5 = node_group.nodes.new('NodeGroupInput')
    input_node_5.parent = frame_offset
    named_attribute_node_2 = node_group.nodes.new(type='GeometryNodeInputNamedAttribute')
    named_attribute_node_2.inputs[0].default_value = 'distance'
    named_attribute_node_2.parent = frame_offset
    input_node_6 = node_group.nodes.new('NodeGroupInput')
    input_node_6.parent = frame_offset
    power_node = node_group.nodes.new(type='ShaderNodeMath')
    power_node.operation = 'POWER'
    power_node.inputs[1].default_value = 2
    power_node.parent = frame_offset
    multiply_node_2 = node_group.nodes.new(type='ShaderNodeMath')
    multiply_node_2.operation = 'MULTIPLY'
    multiply_node_2.parent = frame_offset
    multiply_node_3 = node_group.nodes.new(type='ShaderNodeMath')
    multiply_node_3.operation = 'MULTIPLY'
    multiply_node_3.parent = frame_offset
    multiply_node_4 = node_group.nodes.new(type='ShaderNodeMath')
    multiply_node_4.operation = 'MULTIPLY'
    multiply_node_4.inputs[1].default_value = 0.1
    multiply_node_4.parent = frame_offset
    power_node_2 = node_group.nodes.new(type='ShaderNodeMath')
    power_node_2.operation = 'POWER'
    power_node_2.inputs[0].default_value = 2.718
    power_node_2.parent = frame_offset
    divide_node = node_group.nodes.new(type='ShaderNodeMath')
    divide_node.operation = 'DIVIDE'
    divide_node.parent = frame_offset
    subtract_node_6 = node_group.nodes.new(type='ShaderNodeMath')
    subtract_node_6.operation = 'SUBTRACT'
    subtract_node_6.parent = frame_offset
    multiply_node_5 = node_group.nodes.new(type='ShaderNodeMath')
    multiply_node_5.operation = 'MULTIPLY'
    multiply_node_5.parent = frame_offset
    named_attribute_node_3 = node_group.nodes.new(type='GeometryNodeInputNamedAttribute')
    named_attribute_node_3.data_type = 'BOOLEAN'
    named_attribute_node_3.inputs[0].default_value = 'is_interspersed'
    named_attribute_node_3.parent = frame_offset
    add_node = node_group.nodes.new(type='ShaderNodeMath')
    add_node.operation = 'ADD'
    add_node.parent = frame_offset
    switch_node = node_group.nodes.new(type='GeometryNodeSwitch')
    switch_node.input_type = 'FLOAT'
    switch_node.parent = frame_offset
    blur_attribute_node_2 = node_group.nodes.new(type='GeometryNodeBlurAttribute')
    blur_attribute_node_2.inputs[4].default_value = 100
    blur_attribute_node_2.parent = frame_offset
    ## root direction
    evaluate_on_domain_node_2 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_2.data_type = 'INT'
    evaluate_on_domain_node_2.domain = 'CURVE'
    evaluate_on_domain_node_2.parent = frame_offset
    curve_tangent_node = node_group.nodes.new(type='GeometryNodeInputTangent')
    curve_tangent_node.parent = frame_offset
    evaluate_at_index_node_3 = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node_3.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node_3.parent = frame_offset
    evaluate_on_domain_node_3 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_3.data_type = 'FLOAT_VECTOR'
    evaluate_on_domain_node_3.domain = 'CURVE'
    evaluate_on_domain_node_3.parent = frame_offset
    point_of_curve_node_2 = node_group.nodes.new(type='GeometryNodePointsOfCurve')
    point_of_curve_node_2.parent = frame_offset
    scale_node = node_group.nodes.new(type='ShaderNodeVectorMath')
    scale_node.operation = 'SCALE'
    scale_node.parent = frame_offset

    scale_node.location = Vector((23.0* width, -9.0 * height))
    evaluate_on_domain_node_3.location = Vector((21.5 * width, -9.0 * height))
    evaluate_at_index_node_3.location = Vector((20.0 * width, -9.0 * height))
    evaluate_on_domain_node_2.location = Vector((18.5 * width, -9.0 * height))
    curve_tangent_node.location = Vector((18.5 * width, -10.5 * height))
    blur_attribute_node_2.location = Vector((21.5 * width, -11.5 * height))
    switch_node.location = Vector((20.0 * width, -11.5 * height))
    named_attribute_node_3.location = Vector((18.5 * width, -11.5 * height))
    add_node.location = Vector((18.5 * width, -13.0 * height))
    subtract_node_6.location = Vector((17.0 * width, -10.0 * height))
    point_of_curve_node_2.location = Vector((17.0 * width, -8.5 * height))
    multiply_node_3.location = Vector((14.75 * width, -9.0 * height))
    multiply_node_4.location = Vector((14.75 * width, -11.5 * height))
    multiply_node_5.location = Vector((17.0 * width, -13.5 * height))
    divide_node.location = Vector((15.5 * width, -14.0 * height))
    power_node_2.location = Vector((14.0 * width, -14.5 * height))
    named_attribute_node_2.location = Vector((12.5 * width, -9.0 * height))
    input_node_6.location = Vector((12.5 * width, -10.5 * height))
    power_node.location = Vector((12.5 * width, -12.5 * height))
    multiply_node_2.location = Vector((12.5 * width, -14.5 * height))
    spline_parameter_node_2.location = Vector((11.0 * width, -13.0 * height))
    input_node_5.location = Vector((11.0 * width, -14.5 * height))

    # Root Reset
    frame_rr = node_group.nodes.new("NodeFrame")
    frame_rr.label = "Root Reset"
    input_node_7 = node_group.nodes.new('NodeGroupInput')
    input_node_7.parent = frame_rr
    object_info_node_3 = node_group.nodes.new(type='GeometryNodeObjectInfo')
    object_info_node_3.transform_space = 'RELATIVE'
    object_info_node_3.parent = frame_rr
    position_node_7 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_7.parent = frame_rr
    sample_nearest_surface_node_3 = node_group.nodes.new(type='GeometryNodeSampleNearestSurface')
    sample_nearest_surface_node_3.data_type = 'FLOAT_VECTOR'
    sample_nearest_surface_node_3.parent = frame_rr
    endpoint_selection_node_2 = node_group.nodes.new(type='GeometryNodeCurveEndpointSelection')
    endpoint_selection_node_2.inputs[0].default_value = 1
    endpoint_selection_node_2.inputs[1].default_value = 0
    endpoint_selection_node_2.parent = frame_rr

    endpoint_selection_node_2.location = Vector((26.0 * width, -1.5 * height))
    sample_nearest_surface_node_3.location = Vector((26.0 * width, 0.5 * height))
    position_node_7.location = Vector((24.5 * width, -0.5 * height))
    object_info_node_3.location = Vector((24.5 * width, 1.5 * height))
    input_node_7.location = Vector((23.0 * width, 1.5 * height))

    # Restore Segment Lengths
    frame_rsl = node_group.nodes.new("NodeFrame")
    frame_rsl.label = "Restore Segment Lengths"
    point_of_curve_node_3 = node_group.nodes.new(type='GeometryNodePointsOfCurve')
    point_of_curve_node_3.parent = frame_rsl
    evaluate_on_domain_node_4 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_4.data_type = 'INT'
    evaluate_on_domain_node_4.domain = 'CURVE'
    evaluate_on_domain_node_4.parent = frame_rsl
    position_node_8 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_8.parent = frame_rsl
    evaluate_at_index_node_4 = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node_4.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node_4.parent = frame_rsl
    evaluate_on_domain_node_5 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_5.data_type = 'FLOAT_VECTOR'
    evaluate_on_domain_node_5.domain = 'CURVE'
    evaluate_on_domain_node_5.parent = frame_rsl
    curve_of_point_node = node_group.nodes.new(type='GeometryNodeCurveOfPoint')
    curve_of_point_node.parent = frame_rsl
    index_node = node_group.nodes.new(type='GeometryNodeInputIndex')
    index_node.parent = frame_rsl
    equal_node = node_group.nodes.new(type='FunctionNodeCompare')
    equal_node.operation = 'EQUAL'
    equal_node.data_type = 'INT'
    equal_node.parent = frame_rsl
    subtract_node_7 = node_group.nodes.new(type='ShaderNodeMath')
    subtract_node_7.operation = 'SUBTRACT'
    subtract_node_7.inputs[1].default_value = 1
    subtract_node_7.parent = frame_rsl
    switch_node_2 = node_group.nodes.new(type='GeometryNodeSwitch')
    switch_node_2.input_type = 'INT'
    switch_node_2.parent = frame_rsl
    evaluate_at_index_node_5 = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node_5.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node_5.parent = frame_rsl
    distance_node = node_group.nodes.new(type='ShaderNodeVectorMath')
    distance_node.operation = 'DISTANCE'
    distance_node.parent = frame_rsl
    mix_node = node_group.nodes.new(type='ShaderNodeMix')
    mix_node.inputs[0].default_value = 1.0
    mix_node.parent = frame_rsl
    scale_node_2 = node_group.nodes.new(type='ShaderNodeVectorMath')
    scale_node_2.operation = 'SCALE'
    scale_node_2.parent = frame_rsl
    accumulate_field_node = node_group.nodes.new(type='GeometryNodeAccumulateField')
    accumulate_field_node.data_type = 'FLOAT_VECTOR'
    accumulate_field_node.parent = frame_rsl
    curve_of_point_node_2 = node_group.nodes.new(type='GeometryNodeCurveOfPoint')
    curve_of_point_node_2.parent = frame_rsl
    evaluate_on_domain_node_6 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_6.data_type = 'BOOLEAN'
    evaluate_on_domain_node_6.domain = 'CURVE'
    evaluate_on_domain_node_6.inputs[4].default_value = True
    evaluate_on_domain_node_6.parent = frame_rsl
    index_node_2 = node_group.nodes.new(type='GeometryNodeInputIndex')
    index_node_2.parent = frame_rsl
    offset_point_on_curve_node = node_group.nodes.new(type='GeometryNodeOffsetPointInCurve')
    offset_point_on_curve_node.inputs[1].default_value = -1
    offset_point_on_curve_node.parent = frame_rsl
    switch_node_3 = node_group.nodes.new(type='GeometryNodeSwitch')
    switch_node_3.input_type = 'INT'
    switch_node_3.parent = frame_rsl
    position_node_9 = node_group.nodes.new(type='GeometryNodeInputPosition')
    position_node_9.parent = frame_rsl
    evaluate_at_index_node_6 = node_group.nodes.new(type='GeometryNodeFieldAtIndex')
    evaluate_at_index_node_6.data_type = 'FLOAT_VECTOR'
    evaluate_at_index_node_6.parent = frame_rsl
    subtract_node_8 = node_group.nodes.new(type='ShaderNodeVectorMath')
    subtract_node_8.operation = 'SUBTRACT'
    subtract_node_8.parent = frame_rsl
    evaluate_on_domain_node_7 = node_group.nodes.new(type='GeometryNodeFieldOnDomain')
    evaluate_on_domain_node_7.data_type = 'FLOAT_VECTOR'
    evaluate_on_domain_node_7.parent = frame_rsl
    length_node = node_group.nodes.new(type='ShaderNodeVectorMath')
    length_node.operation = 'LENGTH'
    length_node.parent = frame_rsl
    normalize_node = node_group.nodes.new(type='ShaderNodeVectorMath')
    normalize_node.operation = 'NORMALIZE'
    normalize_node.parent = frame_rsl
    switch_node_4 = node_group.nodes.new(type='GeometryNodeSwitch')
    switch_node_4.input_type = 'FLOAT'
    switch_node_4.parent = frame_rsl
    switch_node_5 = node_group.nodes.new(type='GeometryNodeSwitch')
    switch_node_5.input_type = 'VECTOR'
    switch_node_5.parent = frame_rsl

    point_of_curve_node_3.location = Vector((34.5 * width, -9.0 * height))
    evaluate_on_domain_node_4.location = Vector((36.0 * width, -9.0 * height))
    position_node_8.location = Vector((36.0 * width, -10.5 * height))
    evaluate_at_index_node_4.location = Vector((37.5 * width, -9.0 * height))
    evaluate_on_domain_node_5.location = Vector((39.0 * width, -9.0 * height))
    curve_of_point_node.location = Vector((25.5 * width, -9.0 * height))
    index_node.location = Vector((25.5 * width, -10.5 * height))
    equal_node.location = Vector((27.0 * width, -9.0 * height))
    subtract_node_7.location = Vector((27.0 * width, -10.5 * height))
    switch_node_2.location = Vector((28.5 * width, -9.0 * height))
    evaluate_at_index_node_5.location = Vector((30.0 * width, -9.0 * height))
    distance_node.location = Vector((31.5 * width, -9.0 * height))
    mix_node.location = Vector((36.0 * width, -11.5 * height))
    scale_node_2.location = Vector((37.5 * width, -11.5 * height))
    accumulate_field_node.location = Vector((39.0 * width, -11.5 * height))
    curve_of_point_node_2.location = Vector((37.5 * width, -13.0 * height))
    evaluate_on_domain_node_6.location = Vector((31.5 * width, -11.0 * height))
    index_node_2.location = Vector((25.5 * width, -12.0 * height))
    offset_point_on_curve_node.location = Vector((25.5 * width, -13.0 * height))
    switch_node_3.location =  Vector((27.0 * width, -12.0 * height))
    position_node_9.location = Vector((27.0 * width, -13.5 * height))
    evaluate_at_index_node_6.location = Vector((28.5 * width, -13.0 * height))
    subtract_node_8.location = Vector((30.0 * width, -12.5 * height))
    evaluate_on_domain_node_7.location = Vector((31.5 * width, -12.5 * height))
    length_node.location = Vector((33.0 * width, -11.0 * height))
    normalize_node.location = Vector((33.0 * width, -12.5 * height))
    switch_node_4.location = Vector((34.5 * width, -11.0 * height))
    switch_node_5.location = Vector((34.5 * width, -12.5 * height))


    # Judges Interspersed-link
    node_group.links.new(input_node.outputs['Head Object'], object_info_node.inputs['Object'])
    node_group.links.new(object_info_node.outputs['Geometry'], geometry_proximity_node.inputs['Target'])
    node_group.links.new(position_node.outputs['Position'], geometry_proximity_node.inputs[1])
    node_group.links.new(position_node.outputs['Position'], subtract_node.inputs[1])
    node_group.links.new(geometry_proximity_node.outputs[0], subtract_node.inputs[0])
    node_group.links.new(object_info_node.outputs['Geometry'], capture_attribute_node.inputs['Geometry'])
    node_group.links.new(normal_node.outputs['Normal'], capture_attribute_node.inputs['Value'])
    node_group.links.new(capture_attribute_node.outputs['Geometry'], sample_nearest_surface_node_2.inputs['Mesh'])
    node_group.links.new(capture_attribute_node.outputs['Attribute'], sample_nearest_surface_node_2.inputs[3])
    node_group.links.new(subtract_node.outputs['Vector'], greater_than_node.inputs[4])
    node_group.links.new(sample_nearest_surface_node_2.outputs[2], greater_than_node.inputs[5])

    # main-link
    node_group.links.new(input_node_2.outputs['Geometry'], capture_attribute_node_2.inputs['Geometry'])
    node_group.links.new(position_node_2.outputs['Position'], capture_attribute_node_2.inputs['Value'])
    node_group.links.new(capture_attribute_node_2.outputs['Geometry'], store_named_attribute_node.inputs['Geometry'])
    node_group.links.new(capture_attribute_node_2.outputs['Attribute'], evaluate_at_index_node_5.inputs[3])
    node_group.links.new(capture_attribute_node_2.outputs['Attribute'], distance_node.inputs[1])
    node_group.links.new(greater_than_node.outputs['Result'], store_named_attribute_node.inputs[6])
    node_group.links.new(store_named_attribute_node.outputs['Geometry'], store_named_attribute_node_2.inputs['Geometry'])
    node_group.links.new(greater_than_node.outputs['Result'], store_named_attribute_node_2.inputs['Selection'])
    node_group.links.new(geometry_proximity_node.outputs['Distance'], store_named_attribute_node_2.inputs[4])
    node_group.links.new(store_named_attribute_node_2.outputs['Geometry'], set_position_node.inputs['Geometry'])
    node_group.links.new(raycast_node.outputs['Hit Position'], set_position_node.inputs['Position'])
    node_group.links.new(and_node.outputs['Boolean'], set_position_node.inputs['Selection'])
    node_group.links.new(set_position_node.outputs['Geometry'], resample_node.inputs['Curve'])
    node_group.links.new(resample_node.outputs['Curve'], set_position_node_2.inputs['Geometry'])
    node_group.links.new(subtract_node_5.outputs[0], set_position_node_2.inputs['Offset'])
    node_group.links.new(set_position_node_2.outputs['Geometry'], set_position_node_3.inputs['Geometry'])
    node_group.links.new(set_position_node_3.outputs['Geometry'], set_position_node_4.inputs['Geometry'])
    node_group.links.new(scale_node.outputs[0], set_position_node_3.inputs['Offset'])
    node_group.links.new(set_position_node_4.outputs['Geometry'], set_position_node_5.inputs['Geometry'])
    node_group.links.new(endpoint_selection_node_2.outputs[0],set_position_node_4.inputs['Selection'])
    node_group.links.new(sample_nearest_surface_node_3.outputs[2], set_position_node_4.inputs['Position'])
    node_group.links.new(set_position_node_5.outputs['Geometry'], output_node.inputs['Geometry'])
    node_group.links.new(evaluate_on_domain_node_5.outputs[2], set_position_node_5.inputs['Position'])
    node_group.links.new(accumulate_field_node.outputs['Leading'], set_position_node_5.inputs['Offset'])

    # move on surface-link
    node_group.links.new(input_node_3.outputs['Head Object'], object_info_node_2.inputs['Object'])
    node_group.links.new(position_node_4.outputs['Position'], separate_node.inputs['Vector'])
    node_group.links.new(position_node_4.outputs['Position'], subtract_node_2.inputs[0])
    node_group.links.new(object_info_node_2.outputs['Location'], separate_node_2.inputs['Vector'])
    node_group.links.new(object_info_node_2.outputs['Geometry'], raycast_node.inputs['Target Geometry'])
    node_group.links.new(separate_node.outputs['Y'], combine_node.inputs['Y'])
    node_group.links.new(separate_node_2.outputs['X'], combine_node.inputs['X'])
    node_group.links.new(separate_node_2.outputs['Z'], combine_node.inputs['Z'])
    node_group.links.new(combine_node.outputs['Vector'], subtract_node_2.inputs[1])
    node_group.links.new(subtract_node_2.outputs['Vector'], raycast_node.inputs['Ray Direction'])
    node_group.links.new(position_node_3.outputs['Position'], raycast_node.inputs['Source Position'])

    # Blurred Position Attribute-link
    node_group.links.new(not_node.outputs[0], multiply_node.inputs[1])
    node_group.links.new(spline_parameter_node.outputs[0], multiply_node.inputs[0])
    node_group.links.new(position_node_5.outputs['Position'], blur_attribute_node.inputs[2])
    node_group.links.new(input_node_4.outputs['Blur Iterations'], blur_attribute_node.inputs['Iterations'])
    node_group.links.new(multiply_node.outputs[0], blur_attribute_node.inputs['Weight'])
    node_group.links.new(point_of_curve_node.outputs[0], evaluate_on_domain_node.inputs[1])
    node_group.links.new(blur_attribute_node.outputs[2], evaluate_at_index_node_2.inputs[3])
    node_group.links.new(evaluate_on_domain_node.outputs[1], evaluate_at_index_node.inputs['Index'])
    node_group.links.new(evaluate_on_domain_node.outputs[1], evaluate_at_index_node_2.inputs['Index'])
    node_group.links.new(capture_attribute_node_2.outputs['Attribute'], evaluate_at_index_node.inputs[3])
    node_group.links.new(evaluate_at_index_node.outputs[2], subtract_node_3.inputs[0])
    node_group.links.new(evaluate_at_index_node_2.outputs[2], subtract_node_3.inputs[1])
    node_group.links.new(subtract_node_3.outputs[0], subtract_node_4.inputs[1])
    node_group.links.new(blur_attribute_node.outputs[2], subtract_node_4.inputs[0])
    node_group.links.new(subtract_node_4.outputs[0], subtract_node_5.inputs[0])
    node_group.links.new(position_node_6.outputs[0], subtract_node_5.inputs[1])

    # not select root-link
    node_group.links.new(endpoint_selection_node.outputs['Selection'], not_node.inputs['Boolean'])
    node_group.links.new(not_node.outputs['Boolean'], and_node.inputs[1])
    node_group.links.new(named_attribute_node.outputs[3], and_node.inputs[0])

    # offset-link
    node_group.links.new(spline_parameter_node_2.outputs['Length'], power_node.inputs[0])
    node_group.links.new(spline_parameter_node_2.outputs['Length'], multiply_node_2.inputs[0])
    node_group.links.new(input_node_5.outputs['Fluffy Position'], multiply_node_2.inputs[1])
    node_group.links.new(input_node_5.outputs['Fluffy Intensity'],multiply_node_5.inputs[1])
    node_group.links.new(named_attribute_node_2.outputs[1], multiply_node_3.inputs[0])
    node_group.links.new(input_node_6.outputs['Intensity'], multiply_node_3.inputs[1])
    node_group.links.new(power_node.outputs[0], multiply_node_4.inputs[0])
    node_group.links.new(multiply_node_2.outputs[0], power_node_2.inputs[1])
    node_group.links.new(multiply_node_2.outputs[0], divide_node.inputs[0])
    node_group.links.new(power_node_2.outputs[0], divide_node.inputs[1])
    node_group.links.new(divide_node.outputs[0], multiply_node_5.inputs[0])
    node_group.links.new(multiply_node_5.outputs[0],add_node.inputs[1])
    node_group.links.new(multiply_node_3.outputs[0], subtract_node_6.inputs[0])
    node_group.links.new(multiply_node_4.outputs[0], subtract_node_6.inputs[1])
    node_group.links.new(subtract_node_6.outputs[0], add_node.inputs[0])
    node_group.links.new(add_node.outputs[0], switch_node.inputs['True'])
    node_group.links.new(named_attribute_node_3.outputs[3], switch_node.inputs['Switch'])
    node_group.links.new(switch_node.outputs[0], blur_attribute_node_2.inputs[0])
    node_group.links.new(blur_attribute_node_2.outputs[0], scale_node.inputs[3])
    node_group.links.new(evaluate_on_domain_node_3.outputs[2], scale_node.inputs[0])
    node_group.links.new(evaluate_at_index_node_3.outputs[2], evaluate_on_domain_node_3.inputs[2])
    node_group.links.new(evaluate_on_domain_node_2.outputs[1], evaluate_at_index_node_3.inputs[0])
    node_group.links.new(curve_tangent_node.outputs[0], evaluate_at_index_node_3.inputs[3])
    node_group.links.new(point_of_curve_node_2.outputs[0], evaluate_on_domain_node_2.inputs[1])

    # root reset-link
    node_group.links.new(input_node_7.outputs['Head Object'], object_info_node_3.inputs[0])
    node_group.links.new(object_info_node_3.outputs['Geometry'], sample_nearest_surface_node_3.inputs['Mesh'])
    node_group.links.new(position_node_7.outputs[0], sample_nearest_surface_node_3.inputs[3])

    # Restore Segment Lengths-link
    node_group.links.new(curve_of_point_node.outputs[0], equal_node.inputs[2])
    node_group.links.new(index_node.outputs[0], subtract_node_7.inputs[0])
    node_group.links.new(index_node.outputs[0], switch_node_2.inputs[5])
    node_group.links.new(subtract_node_7.outputs[0], switch_node_2.inputs[4])
    node_group.links.new(equal_node.outputs[0], switch_node_2.inputs['Switch'])
    node_group.links.new(switch_node_2.outputs[1], evaluate_at_index_node_5.inputs[0])
    node_group.links.new(evaluate_at_index_node_5.outputs[2], distance_node.inputs[0])
    node_group.links.new(distance_node.outputs[1], mix_node.inputs[3])
    node_group.links.new(point_of_curve_node_3.outputs[0], evaluate_on_domain_node_4.inputs[1])
    node_group.links.new(evaluate_on_domain_node_4.outputs[1],evaluate_at_index_node_4.inputs[0])
    node_group.links.new(evaluate_at_index_node_4.outputs[2], evaluate_on_domain_node_5.inputs[2])
    node_group.links.new(position_node_8.outputs[0], evaluate_at_index_node_4.inputs[3])
    node_group.links.new(index_node_2.outputs[0], switch_node_3.inputs[4])
    node_group.links.new(offset_point_on_curve_node.outputs[0], switch_node_3.inputs[0])
    node_group.links.new(offset_point_on_curve_node.outputs[1], switch_node_3.inputs[5])
    node_group.links.new(switch_node_3.outputs[1], evaluate_at_index_node_6.inputs[0])
    node_group.links.new(position_node_9.outputs['Position'], evaluate_at_index_node_6.inputs[3])
    node_group.links.new(evaluate_at_index_node_6.outputs[2], subtract_node_8.inputs[1])
    node_group.links.new(position_node_9.outputs['Position'], subtract_node_8.inputs[0])
    node_group.links.new(subtract_node_8.outputs[0], evaluate_on_domain_node_7.inputs[2])
    node_group.links.new(evaluate_on_domain_node_7.outputs[2], length_node.inputs[0])
    node_group.links.new(evaluate_on_domain_node_7.outputs[2], normalize_node.inputs[0])
    node_group.links.new(evaluate_on_domain_node_6.outputs[4], switch_node_4.inputs[0])
    node_group.links.new(length_node.outputs[1], switch_node_4.inputs[3])
    node_group.links.new(evaluate_on_domain_node_6.outputs[4], switch_node_5.inputs[0])
    node_group.links.new(normalize_node.outputs[0], switch_node_5.inputs[9])
    node_group.links.new(switch_node_4.outputs[0], mix_node.inputs[2])
    node_group.links.new(mix_node.outputs['Result'], scale_node_2.inputs['Scale'])
    node_group.links.new(switch_node_5.outputs[3], scale_node_2.inputs[0])
    node_group.links.new(scale_node_2.outputs[0], accumulate_field_node.inputs[0])
    node_group.links.new(curve_of_point_node_2.outputs[0], accumulate_field_node.inputs['Group ID'])

    return node_group
