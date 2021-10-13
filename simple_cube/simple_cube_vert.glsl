#version 450

layout(location=0)in vec3 vertex;
layout(location=1)in vec3 vert_color;
layout(location=0)out vec3 color;
uniform mat4 mvp;

void main(){
    color=vert_color;
    gl_Position=mvp*vec4(vertex,1.);
}