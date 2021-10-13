#version 410

layout(location=0)in vec2 vertex;
layout(location=1)in vec3 vert_color;
layout(location=0)out vec3 color;

void main(){
    color=vert_color;
    gl_Position=vec4(vertex,1.,1.);
}