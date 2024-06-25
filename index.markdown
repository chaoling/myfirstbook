---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

<h1>Welcome to My First Book</h1>

<a href="{{ site.baseurl }}{% assign first_post = site.posts | sort: 'date' | first %}{{ first_post.url }}">Start Reading Chapter 1</a>

<h2 class="post-list-heading">Posts</h2>
<ul class="post-list">
  {% for post in site.posts %}
    <li>
      <span class="post-meta">{{ post.date | date: "%b %-d, %Y" }}</span>
      <h3>
        <a class="post-link" href="{{ post.url | relative_url }}">{{ post.title }}</a>
      </h3>
    </li>
  {% endfor %}
</ul>
