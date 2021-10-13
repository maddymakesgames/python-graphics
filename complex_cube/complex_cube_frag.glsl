#version 450

layout(location=0)out vec4 frag_color;
layout(location=0)in vec3 color;
layout(location=1)in vec2 uv;
uniform sampler2DRect tex;
uniform vec2 image_dims;

void main(){
    vec3 tex_color=texture(tex,uv * image_dims).rgb;
    frag_color=vec4(tex_color + (color / 10),1.);
}