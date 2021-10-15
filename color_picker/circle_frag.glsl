#version 410

layout(location=0)out vec4 frag_color;
layout(location=1)in vec3 color;
layout(location=0)in vec2 position;

uniform vec2 center;
uniform float inner_radius;
uniform float outer_radius;
uniform vec2 mouse_coords;

#define SV vec2(1.0, 1.0)
#define PI 3.14159265

/*
This shader could be a lot shorter if we rendered multiple objects instead of just one quad

This is all in one shader as the point of this is to provide an example of a more complex shader
*/

vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0 );
    rgb = rgb*rgb*(3.0-2.0*rgb);
    return c.z * mix( vec3(1.0), rgb, c.y);
}

float point_sign(vec2 a, vec2 b, vec2 c) {
    return (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y);
}

bool is_in_triangle(vec2[3] triangle, vec2 position) {

    float d1 = point_sign(position, triangle[0], triangle[1]);
    float d2 = point_sign(position, triangle[1], triangle[2]);
    float d3 = point_sign(position, triangle[2], triangle[0]);

    bool has_neg = (d1 < 0) || (d2 < 0) || (d3 < 0);
    bool has_pos = (d1 > 0) || (d2 > 0) || (d3 > 0);

    return !(has_neg && has_pos);
}


vec2 gen_triangle_point(vec2 start_point, vec2 center, float angle) {
    return start_point * mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
}

vec2[3] gen_triangle(float radius) {
    float mouse_angle = atan(mouse_coords.y, mouse_coords.x);
    vec2 a = vec2(radius * cos(mouse_angle), radius * sin(mouse_angle));
    vec2 b = gen_triangle_point(a, center, radians(120.));
    vec2 c = gen_triangle_point(a, center, radians(360.-120.));

    return vec2[](a, b, c);
}

bool line_check(vec2 a, vec2 b, vec2 curr, float tolerance) {
    float dxc = curr.x - a.x;
    float dyc = curr.y - a.y;

    float dx1 = b.x - a.x;
    float dy1 = b.y - a.y;

    float on_check = dxc * dy1 - dyc * dx1;

    if(abs(on_check) > tolerance) {
        return false;
    }

    if(abs(dx1) >= abs(dy1)) {
        return dx1 > 0 ?
            a.x <= curr.x && curr.x <= b.x :
            b.x <= curr.x && curr.x <= a.x;
    } else {
        return dy1 > 0 ?
            a.y <= curr.y && curr.y <= b.y :
            b.y <= curr.y && curr.y <= a.y;
    }
}

bool triangle_line_check(vec2[3] points, vec2 position, float tolerance) {
    return line_check(points[0], points[1], position, tolerance)
        || line_check(points[0], points[2], position, tolerance)
        || line_check(points[1], points[2], position, tolerance);
}

float get_angle(vec2 point) {
    return atan(point.x, point.y)*PI*0.05;
}

vec3 point_hsv_combine_hue(vec2[3] triangle, vec2 position) {
    float a_angle = get_angle(triangle[0]);
    float b_angle = get_angle(triangle[1]);
    float c_angle = get_angle(triangle[2]);

    float a_dist = (1 - distance(triangle[0], position)) * 4.;
    float b_dist = (1 - distance(triangle[1], position)) * 4.;
    float c_dist = (1 - distance(triangle[2], position)) * 4.;

    vec3 a_color = a_dist * hsv2rgb(vec3(a_angle, 1., 1.));
    vec3 b_color = b_dist * hsv2rgb(vec3(b_angle, 1., 1.));
    vec3 c_color = c_dist * hsv2rgb(vec3(c_angle, 1., 1.));

    return a_color + b_color + c_color;
}

vec3 point_hsv_sv(vec2[3] triangle, vec2 position) {
    float b = distance(triangle[1], position);
    float c = distance(triangle[2], position);

    return hsv2rgb(vec3(get_angle(triangle[0]), b, c));
}

// Switch which line is commented to switch the triangle's color mode
vec3 get_point_hsv(vec2[3] triangle, vec2 position) {
    // return point_hsv_combine_hue(triangle, position);
    return point_hsv_sv(triangle, position);
}




void main(){
    float frag_distance = distance(position, center);

    float angle = atan(position.x, position.y)*PI*0.05;
    float mouse_angle = atan(mouse_coords.x, mouse_coords.y)*PI*0.05;
    vec3 rgb = hsv2rgb(vec3(angle, SV));

    vec2[3] triangle = gen_triangle(inner_radius * 1.01);

    if(frag_distance > inner_radius && frag_distance < outer_radius) 
        frag_color=vec4(rgb,1.);
    else if(triangle_line_check(triangle, position, 0.03))
        frag_color = vec4(1.,1.,1.,1.);
    else if(is_in_triangle(triangle, position)) {
        frag_color = vec4(get_point_hsv(triangle, position),1.);
    }
    else
        discard;
}