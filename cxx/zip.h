//---
//Copyright (C) 2013 Sebastian Mach. mach.seb at gmail dot com
//
//Distributed under the Boost Software License, Version 1.0.
//(See accompanying file LICENSE_1_0.txt or copy ath ttp://www.boost.org/LICENSE_1_0.txt)
//---

#ifndef ZIP_H_INCLUDED_20130319
#define ZIP_H_INCLUDED_20130319

#include <tuple>
#include <vector>
#include <algorithm>

namespace ssx {
    namespace detail
    {
        // helper to build/expand a template-argument-list of integers, which is
        // needed to variadically expand std::tuple<> with std::get<>
        template<int ...>         struct int_pack { };
        template<int N, int ...S> struct gen_int_pack : gen_int_pack<N-1, N-1, S...> { };
        template<int ...S>        struct gen_int_pack<0, S...> { typedef int_pack<S...> type; };

        // nop() does nothing, but allows us to unpack argument packs into its
        // argument list.
        template <typename T> inline void nop(T ...) {}                                                   

        // increment a tuple of iterators.
        template <int ...S, typename ...Iters>
        inline
        void inc (int_pack<S...>, std::tuple<Iters...> &iters)
        {
            nop(++std::get<S>(iters)...);
        }

        // emplace the iterator 'pointees' into the passed container.
        template <int ...S, typename ...Iters, typename Cont>
        inline
        void emplace_back (int_pack<S...>, std::tuple<Iters...> const &iters, Cont &cont)
        {
            cont.emplace_back (*std::get<S>(iters)...);
        }
    }


    template <template <typename ...> class RetCont = std::vector,
              typename ...Conts>
    inline
      RetCont < std::tuple<typename Conts :: value_type ...> >
      zip(Conts... conts)
    {
        typedef typename detail::gen_int_pack<sizeof...(Conts)>::type indices;

        std::tuple<typename Conts::const_iterator ...> iters(std::begin(conts)...);
        RetCont < std::tuple<typename Conts :: value_type ...> > ret;   
       
        // Use size() functions for performant repetition count,
        // but use iterators to unref values. This lets us support any container,
        // and might be better performing than comparing each iterator with end()
        for (int i=0, reps=std::min({conts.size() ...}); i!=reps; ++i) {
            detail::emplace_back(indices(), iters, ret);       
            detail::inc(indices(), iters);
        }
        return ret;
    }
}

// TODO: have an iterator only version, where the body of the for-statement#
//       goes directly into iterator::operator++() ?


// -- EXAMPLE ------------------------------------------------------------------
//#include <list>
//#include <iostream>
//#include <array>
//#include <deque>
//int main () {
//    std::list<int> ints{{1,2}};
//    const std::vector<float> floats{{10.5,11.5}};
//    const std::array<float,2> more_floats {100.123, 101.123};
//
//    for (auto i : zip(ints, floats, more_floats)) {
//        std::cout << std::get<0>(i) << ", " << std::get<1>(i) << ", " << std::get<2>(i) << std::endl;
//    }
//}

#endif // ZIP_H_INCLUDED_20130319
