#version 120

attribute vec3 aPosition;
attribute vec2 aTexCoord;
attribute vec3 aNormal;

varying vec2 texCoord;
varying vec3 Normal;
varying vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(void)
{
    texCoord = aTexCoord;

    // Упрощенная нормальная матрица (без inverse/transpose для совместимости)
    Normal = aNormal;
    FragPos = vec3(model * vec4(aPosition, 1.0));

    // Правильный порядок умножения матриц
    gl_Position = projection * view * model * vec4(aPosition, 1.0);
}