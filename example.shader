/*
Это пример шейдера для bgfx.
Здесь вы можете просмотреть, как должен быть написан шейдерная программа.
Здесь не надо разделять вершинный и фрагментые шейдера на отдельные файлы,
тут всё вместе.

В varying.def.sc не поддерживаются коментарии, а здесь можно хоть где.
*/
// Сейчас здесь блок инициализации шейдера. Здесь не нужно писать код, только
// переменные, которые будут входными или выходными
$decl input vec2 a_position : POSITION;
$decl input vec4 a_color0 : COLOR0;
$decl output vec4 v_color0 : COLOR0;

$vertex // Это обозначает, что начинается блок вершинного шейдера
uniform mat4  u_modelViewProj;
// Коментарий
/*
Многострочный коментарий в вершинном шейдере
*/
void main()
{
    gl_Position = u_modelViewProj * vec4(a_position, 0.0, 1.0);
	v_color0 = a_color0;
}

$fragment
// Коментарий
/*
Многострочный коментарий в фрагментном шейдере
*/
void main()
{
    gl_FragColor = v_color0;
}