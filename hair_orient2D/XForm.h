#ifndef XFORM_H
#define XFORM_H
/*
 Szymon Rusinkiewicz
 Princeton University
 
 XForm.h
 Transformations (represented internally as column-major 4x4 matrices)
 
 Supports the following operations:
 xform xf, xf2;			// Initialized to the identity
 XForm<float> xf3;		// Just "xform" is XForm<double>
 xf=xform::trans(u,v,w);		// An xform that translates
 xf=xform::rot(ang,ax);		// An xform that rotates
 xf=xform::scale(s);		// An xform that scales
 xf=xform::ortho(l,r,b,t,n,f);   // Like GLortho
 xf=xform::frustum(l,r,b,t,n,f);	// Like GLfrustum
 glMultMatrixd(xf);		// Conversion to column-major array
 bool ok = xf.read("file.xf");	// Read xform from file
 xf.write("file.xf");		// Write xform to file
 xf=xf * xf2;			// Matrix-matrix multiplication
 xf=inv(xf2);			// Inverse
 vec v = xf * vec(1,2,3);	// Matrix-vector multiplication
 xf2=rot_only(xf);		// Just the upper 3x3 of xf
 xf2=trans_only(xf);		// Just the translation of xf
 xf2=norm_xf(xf);		// Inverse transpose, no translation
 invert(xf);			// Inverts xform in place
 orthogonalize(xf);		// Makes matrix orthogonal
 xf(1,2)=3.0;			// Access by row/column
 xf[4]=5.0;			// Access in column-major order
 xfname("file.ply")		// Returns string("file.xf")
 */

#include <iostream>
#include <fstream>
#include <string>
#include "lineqn.h"

template <class T>
class XForm {
private:
	T m[16]; // Column-major (OpenGL) order
    
public:
	// Constructors: defaults to identity
	XForm(const T m0 =1, const T m1 =0, const T m2 =0, const T m3 =0,
	      const T m4 =0, const T m5 =1, const T m6 =0, const T m7 =0,
	      const T m8 =0, const T m9 =0, const T m10=1, const T m11=0,
	      const T m12=0, const T m13=0, const T m14=0, const T m15=1)
	{
		m[0]  = m0;  m[1]  = m1;  m[2]  = m2;  m[3]  = m3;
		m[4]  = m4;  m[5]  = m5;  m[6]  = m6;  m[7]  = m7;
		m[8]  = m8;  m[9]  = m9;  m[10] = m10; m[11] = m11;
		m[12] = m12; m[13] = m13; m[14] = m14; m[15] = m15;
	}
	template <class S> explicit XForm(const S &x)
    { for (int i = 0; i < 16; i++) m[i] = x[i]; }
    
	// Default destructor, copy constructor, assignment operator
    
	// Array reference and conversion to array - no bounds checking
	const T operator [] (int i) const
    { return m[i]; }
	T &operator [] (int i)
    { return m[i]; }
	operator const T * () const
    { return m; }
	operator const T * ()
    { return m; }
	operator T * ()
    { return m; }
    
	// Access by row/column
	const T operator () (int r, int c) const
    { return m[r + c * 4]; }
	T &operator () (int r, int c)
    { return m[r + c * 4]; }
    
	// Some partial compatibility with std::vector
	typedef T value_type;
	typedef T *pointer;
	typedef const T *const_pointer;
	typedef T *iterator;
	typedef const T *const_iterator;
	typedef T &reference;
	typedef const T &const_reference;
	typedef size_t size_type;
	typedef ptrdiff_t difference_type;
    
	size_t size() const
    { return 16; }
	T *begin()
    { return &(m[0]); }
	const T *begin() const
    { return &(m[0]); }
	T *end()
    { return begin() + size(); }
	const T *end() const
    { return begin() + size(); }
    
    
	// Static members - really just fancy constructors
	static XForm<T> identity()
    { return XForm<T>(); }
	static XForm<T> trans(const T &tx, const T &ty, const T &tz)
    { return XForm<T>(1,0,0,0,0,1,0,0,0,0,1,0,tx,ty,tz,1); }
	template <class S> static XForm<T> trans(const S &t)
    { return XForm<T>::trans(t[0], t[1], t[2]); }
	static XForm<T> rot(const T &angle,
                        const T &rx, const T &ry, const T &rz)
	{
		// Angle in radians, unlike OpenGL
		T l = sqrt(rx*rx+ry*ry+rz*rz);
		if (l == T(0))
			return XForm<T>();
		T l1 = T(1)/l, x = rx*l1, y = ry*l1, z = rz*l1;
		T s = sin(angle), c = cos(angle);
		T xs = x*s, ys = y*s, zs = z*s, c1 = T(1)-c;
		T xx = c1*x*x, yy = c1*y*y, zz = c1*z*z;
		T xy = c1*x*y, xz = c1*x*z, yz = c1*y*z;
		return XForm<T>(xx+c,  xy+zs, xz-ys, 0,
                        xy-zs, yy+c,  yz+xs, 0,
                        xz+ys, yz-xs, zz+c,  0,
                        0, 0, 0, 1);
	}
	template <class S> static XForm<T> rot(const T &angle, const S &axis)
    { return XForm<T>::rot(angle, axis[0], axis[1], axis[2]); }
	static XForm<T> scale(const T &s)
    { return XForm<T>(s,0,0,0,0,s,0,0,0,0,s,0,0,0,0,1); }
	static XForm<T> scale(const T &sx, const T &sy, const T &sz)
    { return XForm<T>(sx,0,0,0,0,sy,0,0,0,0,sz,0,0,0,0,1); }
	static XForm<T> scale(const T &s, const T &dx, const T &dy, const T &dz)
	{
		T dlen2 = dx*dx + dy*dy + dz*dz;
		T s1 = (s - T(1)) / dlen2;
		return XForm<T>(T(1) + s1*dx*dx, s1*dx*dy, s1*dx*dz, 0,
                        s1*dx*dy, T(1) + s1*dy*dy, s1*dy*dz, 0,
                        s1*dx*dz, s1*dy*dz, T(1) + s1*dz*dz, 0,
                        0, 0, 0, 1);
	}
	template <class S> static XForm<T> scale(const T &s, const S &dir)
    { return XForm<T>::scale(s, dir[0], dir[1], dir[2]); }
	XForm<T> transpose()
	{
		XForm<T> dir;
		for (int i = 0; i < 4; i++)
			for (int j = 0; j < 4; j++)
			{
				dir[i + 4 * j] = m[j + 4 * i];
			}
		return dir;
	}

	static XForm<T> ortho(const T &l, const T &r, const T &b, const T &t,
                          const T &n, const T &f)
	{
		T rrl = T(1) / (r-l);
		T rtb = T(1) / (t-b);
		T rfn = T(1) / (f-n);
		return XForm<T>(T(2)*rrl, 0, 0, 0,
                        0, T(2)*rtb, 0, 0,
                        0, 0, T(-2)*rfn, 0,
                        -(r+l)*rrl, -(t+b)*rtb, -(f+n)*rfn, 1);
	}
	static XForm<T> frustum(const T &l, const T &r, const T &b, const T &t,
                            const T &n, const T &f)
	{
		T rrl = T(1) / (r-l);
		T rtb = T(1) / (t-b);
		T rfn = T(1) / (f-n);
		return XForm<T>(T(2)*n*rrl, 0, 0, 0,
                        0, T(2)*n*rtb, 0, 0,
                        (r+l)*rrl, (t+b)*rtb, -(f+n)*rfn, -1,
                        0, 0, T(-2)*f*n*rfn, 0);
	}
	// Returns y*x^T, thinking of y and x as column 3-vectors
	template <class S> static XForm<T> outer(const S &y, const S &x)
	{
		XForm<T> result;
		for (int i = 0; i < 3; i++)
			for (int j = 0; j < 3; j++)
				result[4*i+j] = x[i]*y[j];
		return result;
	}
    
	// Read an XForm from a file.
	bool read(const std::string &filename)
	{
		//cout << filename << endl;
		std::ifstream f(filename.c_str());
		//std::ifstream f(filename);
		//ifstream f("F:\\HAIR\\HairSAHM\\Yi\\Yi\\trans\\extrinsic_00008.txt");
		XForm<T> M;
		f >> M;
		if (f.good()) {
 			*this = M;
			f.close();
			return true;
		}
		return false;
	}
    
	// Write an XForm to a file
	bool write(const std::string &filename) const
	{
		std::ofstream f(filename.c_str());
		f << *this;
		f.close();
		return f.good();
	}
};

typedef XForm<double> xform;
typedef XForm<float> fxform;


// Binary operations
template <class T>
static inline XForm<T> operator + (const XForm<T> &xf1, const XForm<T> &xf2)
{
	return XForm<T>(
                    xf1[ 0] + xf2[ 0], xf1[ 1] + xf2[ 1],
                    xf1[ 2] + xf2[ 2], xf1[ 3] + xf2[ 3],
                    xf1[ 4] + xf2[ 4], xf1[ 5] + xf2[ 5],
                    xf1[ 6] + xf2[ 6], xf1[ 7] + xf2[ 7],
                    xf1[ 8] + xf2[ 8], xf1[ 9] + xf2[ 9],
                    xf1[10] + xf2[10], xf1[11] + xf2[11],
                    xf1[12] + xf2[12], xf1[13] + xf2[13],
                    xf1[14] + xf2[14], xf1[15] + xf2[15]
                    );
}

template <class T>
static inline XForm<T> operator - (const XForm<T> &xf1, const XForm<T> &xf2)
{
	return XForm<T>(
                    xf1[ 0] - xf2[ 0], xf1[ 1] - xf2[ 1],
                    xf1[ 2] - xf2[ 2], xf1[ 3] - xf2[ 3],
                    xf1[ 4] - xf2[ 4], xf1[ 5] - xf2[ 5],
                    xf1[ 6] - xf2[ 6], xf1[ 7] - xf2[ 7],
                    xf1[ 8] - xf2[ 8], xf1[ 9] - xf2[ 9],
                    xf1[10] - xf2[10], xf1[11] - xf2[11],
                    xf1[12] - xf2[12], xf1[13] - xf2[13],
                    xf1[14] - xf2[14], xf1[15] - xf2[15]
                    );
}

template <class T>
static inline XForm<T> operator * (const XForm<T> &xf1, const XForm<T> &xf2)
{
	return XForm<T>(
                    xf1[ 0]*xf2[ 0]+xf1[ 4]*xf2[ 1]+xf1[ 8]*xf2[ 2]+xf1[12]*xf2[ 3],
                    xf1[ 1]*xf2[ 0]+xf1[ 5]*xf2[ 1]+xf1[ 9]*xf2[ 2]+xf1[13]*xf2[ 3],
                    xf1[ 2]*xf2[ 0]+xf1[ 6]*xf2[ 1]+xf1[10]*xf2[ 2]+xf1[14]*xf2[ 3],
                    xf1[ 3]*xf2[ 0]+xf1[ 7]*xf2[ 1]+xf1[11]*xf2[ 2]+xf1[15]*xf2[ 3],
                    xf1[ 0]*xf2[ 4]+xf1[ 4]*xf2[ 5]+xf1[ 8]*xf2[ 6]+xf1[12]*xf2[ 7],
                    xf1[ 1]*xf2[ 4]+xf1[ 5]*xf2[ 5]+xf1[ 9]*xf2[ 6]+xf1[13]*xf2[ 7],
                    xf1[ 2]*xf2[ 4]+xf1[ 6]*xf2[ 5]+xf1[10]*xf2[ 6]+xf1[14]*xf2[ 7],
                    xf1[ 3]*xf2[ 4]+xf1[ 7]*xf2[ 5]+xf1[11]*xf2[ 6]+xf1[15]*xf2[ 7],
                    xf1[ 0]*xf2[ 8]+xf1[ 4]*xf2[ 9]+xf1[ 8]*xf2[10]+xf1[12]*xf2[11],
                    xf1[ 1]*xf2[ 8]+xf1[ 5]*xf2[ 9]+xf1[ 9]*xf2[10]+xf1[13]*xf2[11],
                    xf1[ 2]*xf2[ 8]+xf1[ 6]*xf2[ 9]+xf1[10]*xf2[10]+xf1[14]*xf2[11],
                    xf1[ 3]*xf2[ 8]+xf1[ 7]*xf2[ 9]+xf1[11]*xf2[10]+xf1[15]*xf2[11],
                    xf1[ 0]*xf2[12]+xf1[ 4]*xf2[13]+xf1[ 8]*xf2[14]+xf1[12]*xf2[15],
                    xf1[ 1]*xf2[12]+xf1[ 5]*xf2[13]+xf1[ 9]*xf2[14]+xf1[13]*xf2[15],
                    xf1[ 2]*xf2[12]+xf1[ 6]*xf2[13]+xf1[10]*xf2[14]+xf1[14]*xf2[15],
                    xf1[ 3]*xf2[12]+xf1[ 7]*xf2[13]+xf1[11]*xf2[14]+xf1[15]*xf2[15]
                    );
}


// Component-wise equality and inequality (#include the usual caveats
// about comparing floats for equality...)
template <class T>
static inline bool operator == (const XForm<T> &xf1, const XForm<T> &xf2)
{
	for (int i = 0; i < 16; i++)
		if (xf1[i] != xf2[i])
			return false;
	return true;
}

template <class T>
static inline bool operator != (const XForm<T> &xf1, const XForm<T> &xf2)
{
	for (int i = 0; i < 16; i++)
		if (xf1[i] != xf2[i])
			return true;
	return false;
}

template<class T>
static inline XForm<T> transpose(const XForm<T> &xf)
{
    return XForm<T>(xf[0], xf[4], xf[8 ], xf[12],
                    xf[1], xf[5], xf[9 ], xf[13],
                    xf[2], xf[6], xf[10], xf[14],
                    xf[3], xf[7], xf[11], xf[15]);
}

// Inverse
template <class T>
static inline XForm<T> inv(const XForm<T> &xf)
{
	T A[4][4] = { { xf[0], xf[4], xf[8],  xf[12] },
        { xf[1], xf[5], xf[9],  xf[13] },
        { xf[2], xf[6], xf[10], xf[14] },
        { xf[3], xf[7], xf[11], xf[15] } };
	int ind[4];
	bool ok = ludcmp<T,4>(A, ind);
	if (!ok)
		return XForm<T>();
	T B[4][4] = { { 1, 0, 0, 0 },
        { 0, 1, 0, 0 },
        { 0, 0, 1, 0 },
        { 0, 0, 0, 1 } };
	for (int i = 0; i < 4; i++)
		lubksb<T,4>(A, ind, B[i]);
	return XForm<T>(B[0][0], B[0][1], B[0][2], B[0][3],
                    B[1][0], B[1][1], B[1][2], B[1][3],
                    B[2][0], B[2][1], B[2][2], B[2][3],
                    B[3][0], B[3][1], B[3][2], B[3][3]);
}

template <class T>
static inline void invert(XForm<T> &xf)
{
	xf = inv(xf);
}

template <class T>
static inline XForm<T> rot_only(const XForm<T> &xf)
{
	return XForm<T>(xf[0], xf[1], xf[2], 0,
                    xf[4], xf[5], xf[6], 0,
                    xf[8], xf[9], xf[10], 0,
                    0, 0, 0, 1);
}

template <class T>
static inline XForm<T> trans_only(const XForm<T> &xf)
{
	return XForm<T>(1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    xf[12], xf[13], xf[14], 1);
}

template <class T>
static inline XForm<T> norm_xf(const XForm<T> &xf)
{
	XForm<T> M = inv(xf);
	M[12] = M[13] = M[14] = T(0);
	std::swap(M[1], M[4]);
	std::swap(M[2], M[8]);
	std::swap(M[6], M[9]);
	return M;
}

template <class T>
static inline void orthogonalize(XForm<T> &xf)
{
	if (xf[15] == T(0))	// Yuck.  Doesn't make sense...
		xf[15] = T(1);
    
	T q0 = xf[0] + xf[5] + xf[10] + xf[15];
	T q1 = xf[6] - xf[9];
	T q2 = xf[8] - xf[2];
	T q3 = xf[1] - xf[4];
	T l = sqrt(q0*q0+q1*q1+q2*q2+q3*q3);
	
	XForm<T> M = XForm<T>::rot(T(2)*acos(q0/l), q1, q2, q3);
	M[12] = xf[12]/xf[15];
	M[13] = xf[13]/xf[15];
	M[14] = xf[14]/xf[15];
    
	xf = M;
}


// Matrix-vector multiplication
template <class S, class T>
static inline const S operator * (const XForm<T> &xf, const S &v)
{
	T h = xf[3]*v[0] + xf[7]*v[1] + xf[11]*v[2]  + xf[15];
	h = T(1) / h;
    
	return S(T(h*(xf[0]*v[0] + xf[4]*v[1] + xf[8]*v[2]  + xf[12])),
             T(h*(xf[1]*v[0] + xf[5]*v[1] + xf[9]*v[2]  + xf[13])),
             T(h*(xf[2]*v[0] + xf[6]*v[1] + xf[10]*v[2] + xf[14])));
}

// iostream operators
template <class T>
static inline std::ostream &operator << (std::ostream &os, const XForm<T> &m)
{
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			os << m[i+4*j];
			if (j == 3)
				os << std::endl;
			else
				os << " ";
		}
	}
	return os;
}
template <class T>
static inline std::istream &operator >> (std::istream &is, XForm<T> &m)
{

	
	for (int i = 0; i < 3; i++)
		for (int j = 0; j < 4; j++) {
			float mm;
			is >> mm;
			m[i + 4 * j]=mm;
			//cout << mm << "   ";
		}
	if (!is.good()) {
		m = xform::identity();
		return is;
	}
    
	// 4th row is allowed to fail
	for (int j = 0; j < 4; j++)
		is >> m[3+4*j];
	if (!is.good()) {
		m[3] = m[7] = m[11] = T(0);
		m[15] = T(1);
		is.clear();
		return is;
	}
    
	return is;
}

#endif
