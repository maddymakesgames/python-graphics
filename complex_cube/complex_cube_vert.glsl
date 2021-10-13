#version 450

layout(location=0)in vec3 vertex;
layout(location=1)in vec3 vert_color;
layout(location=2)in vec2 vert_uv;
layout(location=0)out vec3 color;
layout(location=1)out vec2 uv;
uniform mat4 mvp;

void main(){
    color=vert_color;
    uv=vert_uv;
    gl_Position=mvp*vec4(vertex,1.);
}